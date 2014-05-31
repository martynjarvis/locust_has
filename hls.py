import random
import requests
import urlparse
import gevent
import time
from locust import events,Locust

import hlslocust.hlserror as hlserror
import hlslocust.cast as cast

BUFFERTIME = 10.0 # time to wait before playing
MAXRETRIES = 2

class HLSLocust(Locust):
    def __init__(self, *args, **kwargs):
        super(HLSLocust, self).__init__(*args, **kwargs)
        self.client = Player()

class HLSObject(object):
    def request(self, name=None):
        if name is None:
            name = self.url # I want to log full url
        start_time = time.time()

        try:
            r = requests.get(self.url)
            r.raise_for_status() # requests wont raise http error for 404 otherwise
        except (requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError, 
                requests.exceptions.Timeout,
                requests.exceptions.TooManyRedirects) as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type="GET", name=name, 
                                        response_time=total_time, exception=e)
        else:
            total_time = int((time.time() - start_time) * 1000)
            try:
                response_length = int(r.headers['Content-Length'])
            except KeyError:
                response_length = 0
                
            events.request_success.fire(request_type="GET", name=name, 
                                        response_time=total_time, 
                                        response_length=response_length)
            return r
        return None

    def download(self):
        r = self.request()
        if r:
            self.parse(r.text)
            return True
        else:
            return False

class MasterPlaylist(HLSObject):
    def __init__(self,name,url,attributes=None):
        self.name=name
        self.url=url
        self.media_playlists = []
        if attributes:
            for k in attributes:
                setattr(self,k,attributes[k])

    def parse(self,manifest):
        self.media_playlists = []
        lines = manifest.split('\n')
        assert(lines[0].startswith('#EXTM3U'))

        for i,line in enumerate(lines):
            if line.startswith('#EXT-X-STREAM-INF'):
                key,val = line.split(':')
                attr = cast.my_cast(val)
                name = lines[i+1].rstrip() # next line 
                url = urlparse.urljoin(self.url, name) # construct absolute url
                self.media_playlists.append(MediaPlaylist(name,url,attr))
            elif line.startswith('#EXT-X-'):
                try:
                    key,val = line.split(':')
                except ValueError:
                    key = line
                    val = True
                key = cast.attr_name(key)
                val = cast.my_cast(val)
                setattr(self,key,val)


class MediaPlaylist(HLSObject):
    def __init__(self,name,url,attributes=None):
        self.name=name
        self.url=url
        self.media_fragments = []
        self.endlist = False
        if attributes:
            for k in attributes:
                setattr(self,k,attributes[k])

    def parse(self,manifest):
        lines = manifest.split('\n')
        assert(lines[0].startswith('#EXTM3U'))
        for i,line in enumerate(lines):
            if line.startswith('#EXTINF'):
                key,val = line.split(':')
                attr = cast.my_cast(val)
                name = lines[i+1].rstrip() # next line
                if not name.startswith('#'):# TODO, bit of a hack here
                    if name not in [x.name for x in self.media_fragments]:
                        url = urlparse.urljoin(self.url, name) # construct absolute url
                        self.media_fragments.append(MediaFragment(name,
                                                                  url,
                                                                  attr,
                                                                  self))

            elif line.startswith('#EXT-X-'): # TODO media sequence special case
                try:
                    key,val = line.split(':')
                except ValueError:
                    key = line
                    val = True
                key = cast.attr_name(key)
                val = cast.my_cast(val)
                setattr(self,key,val)

class MediaFragment(HLSObject):
    def __init__(self,name,url,attributes,parent=None):
        self.url=url
        self.name=name
        self.parent = parent
        self.duration = attributes[0] # only attrib??

    def download(self):
        name = 'Segment ({url})'.format(url=self.parent.url)
        r = self.request(name=name)
        if r:
            return True
        else:
            return False

class Player():
    def __init__(self):
        pass

    def play(self, url=None, quality=None, duration=None):

        # download and parse master playlist
        self.master_playlist = MasterPlaylist('master',url)
        self.master_playlist.download()  

        # I randomly pick a quality, unless it's specified...
        if quality is None:
            playlist = random.choice(self.master_playlist.media_playlists)
        else:
            i = quality%len(self.master_playlist.media_playlists)
            playlist = self.master_playlist.media_playlists[i]

        # download and parse media playlist
        playlist.download()

        start_time = None
        buffer_time = 0.0
        playing = False
        last_manifest_time = time.time()

        idx = 0
        retries = 0

        while True :
            # should I download an object?
            if idx < len(playlist.media_fragments):
                a = playlist.media_fragments[idx]
                r = a.download()
                if r == True:
                    idx+=1
                    buffer_time += a.duration
                else:
                    # TODO, think about this, if I fail to download a single
                    # segment enough times I stop playing. Should I not keep
                    # playing until I run out of buffer the 'buffer underrun'?
                    retries +=1
                    if retries >= MAXRETRIES:
                        play_time = 0
                        if start_time:
                            play_time = (time.time() - start_time)
                        return (buffer_time,play_time)


            # should we start playing?
            if not playing and buffer_time > BUFFERTIME: 
                playing = True
                start_time = time.time()

            if playing:
                # should we grab a new manifest?
                manifest_age = (time.time() - last_manifest_time)
                if manifest_age > playlist.targetduration*2:  # vlc does this
                    r = playlist.download()
                    if r == True:
                        last_manifest_time = time.time()

                play_time = (time.time() - start_time)
                if play_time >= buffer_time:
                    if idx < len(playlist.media_fragments):
                        # we've run out of buffer but we still have parts to
                        # download
                        e = hlserror.BufferUnderrun('Buffer is empty with '
                                                    'files still to download')
                        events.request_failure.fire(request_type="GET",
                                                    name=playlist.url, 
                                                    response_time=play_time,
                                                    exception=e)
                        return (buffer_time,play_time)
                    if playlist.endlist:
                        # we've finished a vod (or live stream ended)
                        return (buffer_time,play_time)
                    else:
                        # we've downloaded and played all the fragments, but
                        # we've not been told that the stream has finished
                        e = hlserror.StaleManifest('Buffer is empty with no '
                                                   'new files to download.')
                        events.request_failure.fire(request_type="GET",
                                                    name=playlist.url, 
                                                    response_time=play_time,
                                                    exception=e)
                        return (buffer_time,play_time)

                # have we seen enough?
                if duration and play_time > duration :
                    return (buffer_time,play_time)
            gevent.sleep(1) # yield execution to another thread


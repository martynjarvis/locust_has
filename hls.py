import random
import requests
import urlparse
import gevent
import time
from locust import events,Locust

BUFFERTIME = 10.0 # time to wait before playing
MAXMANIFESTAGE = 20.0
MAXRETRIES = 2

class HLSLocust(Locust):
    def __init__(self, *args, **kwargs):
        super(HLSLocust, self).__init__(*args, **kwargs)
        self.client = Player()

class HLSObject(object):
    def request(self,name=None):
        start_time = time.time()
        if name is None:
            name = self.url

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
                attr = myCast(val)
                name = lines[i+1].rstrip() # next line 
                url = urlparse.urljoin(self.url, name) # construct absolute url
                self.media_playlists.append(MediaPlaylist(name,url,attr))
            elif line.startswith('#EXT-X-'):
                try:
                    key,val = line.split(':')
                except ValueError:
                    key = line
                    val = True
                key = attrName(key)
                val = myCast(val)
                setattr(self,key,val)


class MediaPlaylist(HLSObject):
    def __init__(self,name,url,attributes=None):
        self.name=name
        self.url=url
        self.media_fragments = []
        if attributes:
            for k in attributes:
                setattr(self,k,attributes[k])

    def parse(self,manifest):
        lines = manifest.split('\n')
        assert(lines[0].startswith('#EXTM3U'))
        for i,line in enumerate(lines):
            if line.startswith('#EXTINF'):
                key,val = line.split(':')
                attr = myCast(val)
                name = lines[i+1].rstrip() # next line
                if not name.startswith('#'):# TODO, bit of a hack here
                    if name not in [x.name for x in self.media_fragments]:
                        url = urlparse.urljoin(self.url, name) # construct absolute url
                        #name = 'Segment ({url})'.format(url=self.url)) # TODO
                        self.media_fragments.append(MediaFragment(name,url,attr))

            elif line.startswith('#EXT-X-'): # TODO media sequence special case
                try:
                    key,val = line.split(':')
                except ValueError:
                    key = line
                    val = True
                key = attrName(key)
                val = myCast(val)
                setattr(self,key,val)

class MediaFragment(HLSObject):
    def __init__(self,name,url,attributes):
        self.url=url
        self.name=name
        self.duration = attributes[0] # only attrib??

    def download(self):
        r = self.request(name=self.name)
        if r:
            return True
        else:
            return False

class Player():
    def __init__(self):
        pass

    def play(self, url=None, quality=None, duration=None):
        baseUrl = url

        # download and parse master playlist
        self.master_playlist = MasterPlaylist('master',baseUrl)
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
                if manifest_age > MAXMANIFESTAGE: 
                    r = playlist.download()
                    if r == True:
                        last_manifest_time = time.time()

                play_time = (time.time() - start_time)
                # am I underrunning?
                if play_time > buffer_time:
                    if idx < len(playlist.media_framgents):
                        # we've run out of buffer but we still have parts to download
                        #TODO fail not exception
                        raise ValueError # underrun
                    # we've finished a vod?
                    #TODO chek for end stream atribute
                    else :
                        return (buffer_time,play_time)
                # have we seen enough?
                if duration and play_time > duration :
                    return (buffer_time,play_time)
            gevent.sleep(1) # yield execution # TODO 1 second? to avoid 100% cpu?

def myBool(a):
    if a.strip().lower()=='no':
        return False
    elif a.strip().lower()=='yes':
        return True
    raise ValueError

def myDict(a):
    a = list(mySplit(a))
    dct = {}
    for b in a:
        key,val = b.split('=')
        key = attrName(key)
        dct[key] = myCast(val)
    return dct

def myList(a):
    a = list(mySplit(a))
    if len(a)>1:
        return [myCast(x) for x in a]
    else:
        raise ValueError

def mySplit(string,sep=','):
    start = 0
    end = 0
    inString = False
    while end < len(string):
        if string[end] not in sep or inString: # mid string
            if string[end] in '\'\"':
                inString = not inString
            end +=1
        else: # separator
            yield string[start:end]
            end +=1
            start = end
    if start != end:# ignore empty items
        yield string[start:end]

def attrName(key):
    return key.replace('#EXT-X-','').replace('-','_').lower()

def myCast(val):
    # intelligent casting ish
    try:
        return int(val)
    except ValueError:
        pass

    try:
        return float(val)
    except ValueError:
        pass

    try:
        return myBool(val)
    except ValueError:
        pass

    try:
        return myDict(val)
    except ValueError:
        pass

    try:
        return myList(val)
    except ValueError:
        pass

    return val


import random
import requests
import urlparse
import gevent
import time
from locust import events,Locust

BUFFERTIME = 10.0 # time to wait before playing
MAXMANIFESTAGE = 20.0

class HLSLocust(Locust):
    def __init__(self, *args, **kwargs):
        super(HLSLocust, self).__init__(*args, **kwargs)
        self.client = Player()

class Player():
    playlists=None
    queue = None
    # TODO, all attr should exist on these objects, rather than player object

    def __init__(self):
        pass

    def request(self,url):
        start_time = time.time()
        try:
            r = requests.get(url)
        except (requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError, 
                requests.exceptions.Timeout,
                requests.exceptions.TooManyRedirects) as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type="GET", name=url, 
                                        response_time=total_time, exception=e)
        else:
            total_time = int((time.time() - start_time) * 1000)
            try:
                response_length = int(r.headers['Content-Length'])
            except KeyError:
                response_length = 0
            events.request_success.fire(request_type="GET", name=url, 
                                        response_time=total_time, 
                                        response_length=response_length)
            return r
        return None

    def play(self, url=None, quality=None):
        baseUrl = url

        # request master playlist
        r = self.request(url)
        if r:
            self.parse(r.text)
        else: 
            return

        # currently I randomly pick a quality, unless it's given...
        if quality is None:
            url = urlparse.urljoin(baseUrl, random.choice(self.playlists).name)
        else:
            i = quality%len(self.playlist)
            url = urlparse.urljoin(baseUrl, self.playlists[i].name)

        # request media playlist
        r = self.request(url)
        if r:
            self.parse(r.text)
        else: 
            return

        # segment loop
        # Currently download segment then 'play' it by sleeping for the length
        # TODO, break out of this loop every 2x target duration to grab updated
        # manifest file.
        # TODO, do this like a client would do.
        start_time = None
        buffer_time = 0.0
        playing = False
        last_manifest_time = time.time()

        idx = 0

        while True :
            # should I download an object?
            if idx < len(self.queue):
                a = self.queue[idx]
                url = urlparse.urljoin(baseUrl, a.name)
                r = self.request(url)
                buffer_time += a.duration
                idx+=1

            # should we start playing?
            if not playing and buffer_time > BUFFERTIME:
                playing = True
                start_time = time.time()

            if playing:
                # should we grab a new manifest?
                manifest_age = (time.time() - last_manifest_time)
                #if manifest_age > MAXMANIFESTAGE: # TODO, new manifest will fill downloaded files here
                    #r = self.request(url)
                    #if r:
                        #self.parse(r.text)

                # am I underrunning?
                play_time = (time.time() - start_time)
                if play_time > buffer_time:
                    if idx < len(self.queue):
                        # we've run out of buffer but we still have parts to download
                        raise ValueError # underrun
                    # we've finished?
                    else :
                        return (buffer_time,play_time)
            gevent.sleep(0) # yield execution

    def parse(self,manifest):

        # remember old playlists
        oldPlaylists = self.playlists
        self.playlists = None

        lines = manifest.split('\n')
        for i,line in enumerate(lines):
            if line.startswith('#'):
                if 'EXT-X-STREAM-INF' in line: # media playlist special case
                    if self.playlists is None:
                        self.playlists = [] # forget old playlists
                    key,val = line.split(':')
                    attr = myCast(val)
                    name = lines[i+1].rstrip() # next line
                    self.playlists.append(MediaPlaylist(name,attr))

                if 'EXTINF' in line: # fragment special case
                    if self.queue is None:
                        self.queue = []
                    key,val = line.split(':')
                    attr = myCast(val)
                    name = lines[i+1].rstrip() # next line
                    if name not in [x.name for x in self.queue]:
                        self.queue.append(MediaFragment(name,attr))

                elif line.startswith('#EXT-X-'):
                    try:
                        key,val = line.split(':')
                    except ValueError:
                        key = line
                        val = True
                    key = attrName(key)
                    val = myCast(val)
                    setattr(self,key,val)

        # playlists weren't updated so keep old playlists
        if self.playlists == None:
            self.playlists = oldPlaylists

        return

class MasterPlaylist():
    pass

class MediaPlaylist():
    def __init__(self,name,attributes):
        self.name = name
        for k in attributes:
            setattr(self,k,attributes[k])

class MediaFragment():
    def __init__(self,name,attributes):
        self.name = name
        self.duration = attributes[0] # only attrib??

def myBool(a):
    if a.strip().lower()=='no':
        return False
    elif a.strip().lower()=='yes':
        return True
    raise ValueError

def myDict(a):
    a = a.split(',')
    dct = {}
    for b in a:
        key,val = b.split('=')
        key = attrName(key)
        dct[key] = myCast(val)
    return dct

def myList(a):
    a = a.split(',')
    if len(a)>1:
        return [myCast(x) for x in a]
    else:
        raise ValueError

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


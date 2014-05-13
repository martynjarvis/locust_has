import random
import requests
import urlparse
import gevent
import time
from locust import events,Locust

class HLSLocust(Locust):
    def __init__(self, *args, **kwargs):
        super(HLSLocust, self).__init__(*args, **kwargs)
        self.client = Player()

class Player():
    playlists=None
    queue = None

    def __init__(self):
        pass

    def request(self,url):
        start_time = time.time()
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type="GET", name=url, 
                                        response_time=total_time, exception=e)
        except requests.exceptions.HTTPError as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type="GET", name=url, 
                                       response_time=total_time, exception=e)
        except requests.exceptions.Timeout as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type="GET", name=url, 
                                        response_time=total_time, exception=e)
        except requests.exceptions.TooManyRedirects  as e:
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
        playtime = 0.0

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
        while len(self.queue) > 0:
            start_time = time.time()
            a = self.queue.pop(0)
            url = urlparse.urljoin(baseUrl, a.name)
            r = self.request(url)
            playtime += a.duration
            total_time = (time.time() - start_time)
            sleep_duration = float(a.duration) - total_time
            if sleep_duration < 0.0:
                raise ValueError # TODO what I'm saying here is that I took >
                                 # segment length to download it. This isn't a
                                 # problem in itself, I need to be smarter here
            gevent.sleep(sleep_duration)

        return playtime


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


import random
import urllib2


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

def attrName(key):
    return key.replace('#EXT-X-','').replace('-','_').lower()

def myList(a):
    a = a.split(',')
    if len(a)>1:
        return [myCast(x) for x in a]
    else:
        raise ValueError

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


class Player():
    playlists=None
    queue = None

    def play(self, url, quality=None):
        f =  urllib2.urlopen(url) 
        self.parse(f.read())                        

        # grab Master Manifest
        # parse it
        # choose random quality, unless given quality
        # grab media playlist
        # playlistFetched = now
        # buffer = 0
        # while true
        #   if download queue is not empty download X fragments (2?, all?, as many as I can in targetduration?)
        #       buffer += downloaded fragments duration 
        #   if now - playListFetched (the age of the playlist) > THRESHOLD (1-4 target durations)
        #       rebuild download queue 
        #   fragment = pop from queue <- if empty throw buffer underrun exception
        #   sleep fragment.duration minus the time it took for this iteration
        return 0


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





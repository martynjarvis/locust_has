
class MasterPlaylist():
    pass

class MediaPlaylist():
    pass

class MediaFragment():
    def __init__(self,name,duration):
        self.name = name
        self.duration = duration


class Player():
    playlists=[]
    queue = [] # download queue
    durations = {}

    def play(self, url, quality=None):
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
        pass


    def parse(self,manifest):
        lines = manifest.split('\n')
        for i,line in enumerate(lines):
            if line.startswith('#'): 
                if 'EXTINF' in line: # fragment special case
                    key,vals = line.split(':')
                    vals = vals.split(',')
                    duration = float(vals[0])
                    name = lines[i+1].rstrip() # next line
                    if name not in [x.name for x in self.queue]: 
                        self.queue.append(MediaFragment(name,duration))

                elif line.startswith('#EXT-X-'):
                    try:
                        key,val = line.split(':')
                    except ValueError:
                        key = line
                        val = True
                    key = key.replace('#EXT-X-','').replace('-','_').lower()
                    
                    # intelligent casting ish
                    try:
                        val = int(val)
                    except ValueError:
                        try:
                            val = float(val)
                        except ValueError:
                            pass

                    setattr(self,key,val)

        return 





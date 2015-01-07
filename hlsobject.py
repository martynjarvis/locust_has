import requests
import urlparse
import time
from locust import events

import hlslocust.asobject as asobject
import hlslocust.hlserror as hlserror
import hlslocust.cast as cast

class MasterPlaylist(asobject.ASManifest):
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
                    key = line[:]
                    val = 'YES'
                key = cast.attr_name(key)
                val = cast.my_cast(val)
                setattr(self,key,val)


class MediaPlaylist(asobject.ASManifest):
    def __init__(self,name,url,attributes=None):
        self.name=name
        self.url=url
        self.media_fragments = []
        self.endlist = False
        if attributes:
            for k in attributes:
                setattr(self,k,attributes[k])

    def parse(self,manifest):
        ms_counter = None
        lines = manifest.split('\n')
        assert(lines[0].startswith('#EXTM3U'))
        for i,line in enumerate(lines):
            if line.startswith('#EXTINF'):
                key,val = line.split(':')
                attr = cast.my_cast(val)
                name = lines[i+1].rstrip() # next line
                if not ms_counter:
                    try:
                        ms_counter = self.media_sequence  # probably live
                    except AttributeError:
                        ms_counter = 1  # probably VOD
                if not name.startswith('#'):
                    # TODO, bit of a hack here. Some manifests put an attribute
                    # line on the first fragment which breaks this.
                    try:
                        last_ms = self.last_media_sequence()
                    except IndexError:
                        last_ms = 0
                    if ms_counter > last_ms:
                        url = urlparse.urljoin(self.url, name) # construct absolute url
                        self.media_fragments.append(
                                asobject.MediaFragment(name, url, attr, self,
                                                       ms_counter))

                ms_counter += 1
            elif line.startswith('#EXT-X-'):
                try:
                    key,val = line.split(':')
                except ValueError:
                    key = line[:]
                    val = 'YES'
                key = cast.attr_name(key)
                val = cast.my_cast(val)
                setattr(self,key,val)

    def first_media_sequence(self):
        # raise index error if no fragments
        return self.media_fragments[0].media_sequence

    def last_media_sequence(self):
        return self.media_fragments[-1].media_sequence

    def get_media_fragment(self, msq):
        idx = msq - self.first_media_sequence()
        if self.media_fragments[idx].media_sequence != msq:
            raise hlserror.MissedFragment('Fragments are not numbered sequentially')
        return self.media_fragments[idx]



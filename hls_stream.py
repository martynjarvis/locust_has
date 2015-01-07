import urlparse

from hlslocust.has_object import Fragment, Stream
import hlslocust.cast as cast

class HLSStream(Stream):
    def __init__(self, url):
        self.base_url = url

    def update(self):
        pass

    def parse(self, manifest):
        for line in (l.strip() for l in manifest.split('#')):
            # TODO what about sinlge bitrate vod streams?
            if line.startswith('EXT-X-STREAM-INF'):
                line1, line2 = line.splitlines()
                key, val = line1.split(':')
                attr = cast.my_cast(val)
                name = line2.rstrip()
                url = urlparse.urljoin(self.base_url, name) # construct absolute url
                # WHAT AM I GOING TO DO WITH THIS URL?!
                # and do I actualy want base url?
                # this is where I should create some data structure to store my
                # url parts
            elif line.startswith('EXT-X-'):
                try:
                    key,val = line.split(':')
                except ValueError:
                    key = line[:]
                    val = 'YES'
                key = cast.attr_name(key)
                val = cast.my_cast(val)
                setattr(self,key,val)


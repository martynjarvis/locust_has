import requests
import urlparse
import time
from locust import events

import hlslocust.hlserror as hlserror # TODO change name of this

class ASObject(object):
    url = ''

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
            if response_length != len(r.content):
                e = hlserror.BadContentLength("content-length header did not match received content length")
                events.request_failure.fire(request_type="GET", name=name,
                                            response_time=total_time,
                                            exception=e)
            events.request_success.fire(request_type="GET", name=name,
                                        response_time=total_time,
                                        response_length=response_length)
            return r
        return None

    def download(self):
        r = self.request()
        if r:
            return True
        else:
            return False

class ASManifest(ASObject):
    def download(self):
        r = self.request()
        if r:
            self.parse(r.text)
            return True
        else:
            return False

    def parse(self,manifest):
        pass

class MediaFragment(ASObject):
    def __init__(self,name,url,attributes,parent=None, seq=None):
        self.url=url
        self.name=name
        self.parent = parent
        self.duration = attributes[0] # only attrib??
        self.media_sequence = seq

    def download(self):
        name = 'Segment ({url})'.format(url=self.parent.url)
        r = self.request(name=name)
        if r:
            return True
        else:
            return False


import random
import gevent
import time
from locust import events, Locust

import hlslocust.hlserror as hlserror
import hlslocust.hlsobject as hlsobject

BUFFERTIME = 10.0 # time to wait before playing
MAXRETRIES = 2

class HLSLocust(Locust):
    def __init__(self, *args, **kwargs):
        super(HLSLocust, self).__init__(*args, **kwargs)
        self.client = Player()

class Player():
    def __init__(self):
        pass

    def play(self, url=None, quality=None, duration=None):

        # download and parse master playlist
        self.master_playlist = hlsobject.MasterPlaylist('master',url)
        r = self.master_playlist.download()  
        if r is False:
            return

        # I randomly pick a quality, unless it's specified...
        if quality is None:
            playlist = random.choice(self.master_playlist.media_playlists)
        else:
            i = quality%len(self.master_playlist.media_playlists)
            playlist = self.master_playlist.media_playlists[i]

        # download and parse media playlist
        r = playlist.download()
        last_manifest_time = time.time()
        if r is False:
            return

        # serves as an index for the fragments
        msq = playlist.first_media_sequence()  

        retries = 0
        start_time = None
        buffer_time = 0.0
        playing = False

        while True :
            # should I download an object?
            if msq <= playlist.last_media_sequence():
                try:
                    a = playlist.get_media_fragment(msq)
                except hlserror.MissedFragment as e:
                    events.request_failure.fire(request_type="GET",
                                                name=playlist.url, 
                                                response_time=play_time,
                                                exception=e)
                    play_time = None
                    if playing:
                        play_time = (time.time() - start_time)
                    return (buffer_time,play_time)

                r = a.download()
                if r == True:
                    msq+=1
                    buffer_time += a.duration
                else:
                    # TODO, think about this, if I fail to download a single
                    # segment enough times I stop playing. Should I not keep
                    # playing until I run out of buffer then 'buffer underrun'?
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
                if not playlist.endlist: # only update manifest on live
                    manifest_age = (time.time() - last_manifest_time)
                    if manifest_age > playlist.targetduration*2:  # vlc does this
                        r = playlist.download()
                        if r == True:
                            last_manifest_time = time.time()

                play_time = (time.time() - start_time)
                if play_time >= buffer_time:
                    if msq <= playlist.last_media_sequence():
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


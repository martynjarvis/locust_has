import time

from hlslocust.buffer import Buffer

# Target buffer length
BUF_LENGTH = 10
MANIFEST_AGE = 10

class Player(object):
    def __init__(self, stream):
        self.stream = stream

    def play(self,bitrate):
        self.stream.update()

        buf = Buffer()
        start_time = None
        duration = 0

        while True:
            if buf.length < BUF_LENGTH:
                fragment = self.stream.get_next_fragment(bitrate)
                fragment.download()
                buf.append(fragment)

            if start_time is None:
                start_time = time.time()

            if duration < (time.time()-start_time):
                # we should start playing a new fragment
                fragment_to_play = buf.pop()
                # index error is a buffer underrun
                duration += fragment_to_play.duration

            if (time.time() - self.stream.last_update) > MANIFEST_AGE:
                self.stream.update()

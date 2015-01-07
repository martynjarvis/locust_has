import time

class Fragment(object):
    def __init__(self, duration):
        self.duration = duration

class Stream(object):
    def __init__(self):
        self.last_update = None

    def update(self):
        self.last_update = time.time()

    def get_next_fragment(self):
        pass


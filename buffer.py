import collections

class Buffer(object):
    def __init__(self):
        self.length = 0
        self.q = collections.deque()

    def pop(self):
        fragment = self.q.popleft()
        self.length -= fragment.duration
        return fragment

    def append(self, fragment):
        self.q.append(fragment)
        self.length += fragment.duration


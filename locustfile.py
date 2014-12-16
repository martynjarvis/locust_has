import random
from locust import TaskSet, task
import hlslocust.hlsplayer as hlsplayer

SECONDS = 1000  # ms in seconds
URL = "http://hout-ciab-live-c9.docroot.yyy11.eng.velocix.com:80/live_hls_sit_{}/hlsmarlin/playlist.m3u8"

class UserBehavior(TaskSet):
    @task
    def play_random(self):
        duration = random.randint(60, 600)
        stream = random.randint(1, 6)
        url = URL.format(stream)
        self.client.play(url, duration=duration)

class HLSUser(hlsplayer.HLSLocust):
    task_set = UserBehavior
    min_wait = 2 * SECONDS  # 2 seconds
    max_wait = 15 * SECONDS  # 5 seconds

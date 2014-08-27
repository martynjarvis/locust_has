import random
from locust import TaskSet, task
import hlslocust.hlsplayer as hlsplayer

SECONDS = 1000  # ms in seconds

class UserBehavior(TaskSet):
    @task
    def play_random(self):
        duration = random.randint(60, 600) 
        self.client.play('http://testsite.zzz106s1.pub/hls/index.m3u8',
                         duration=duration)

class HLSUser(hlsplayer.HLSLocust):
    task_set = UserBehavior
    min_wait = 2 * SECONDS  # 2 seconds
    max_wait = 15 * SECONDS  # 5 seconds

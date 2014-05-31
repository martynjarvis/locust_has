import random
from locust import TaskSet, task

import hlslocust.hls as hls

class UserBehavior(TaskSet):
    @task
    def play_random(self):
        duration = random.randint(60, 600) 
        self.client.play('http://localhost:8000/NTV-Public-IPS.m3u8',
                         duration=duration)

class HLSUser(hls.HLSLocust):
    task_set = UserBehavior
    min_wait=  2*1000 # 2 seconds
    max_wait=  5*1000 # 2 minute

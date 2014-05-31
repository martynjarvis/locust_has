import random
from locust import TaskSet, task

import hlslocust.hlsplayer as hlsplayer

class UserBehavior(TaskSet):
    @task
    def play_random(self):
        #duration = random.randint(600, 1200) 
        duration = 3600
        #self.client.play('http://www.nasa.gov/multimedia/nasatv/NTV-Public-IPS.m3u8',
                         #duration=duration)
        self.client.play('http://devimages.apple.com/iphone/samples/bipbop/bipbopall.m3u8',
                         duration=duration)

class HLSUser(hlsplayer.HLSLocust):
    task_set = UserBehavior
    min_wait=  2*1000 # 2 seconds
    max_wait=  5*1000 # 2 minute

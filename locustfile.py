import random
from locust import TaskSet, task

import hlslocust.hlsplayer as hlsplayer

SECONDS = 1000

class UserBehavior(TaskSet):
    @task
    def play_random(self):
        duration = random.randint(60, 600) 
        #self.client.play('http://testsite.zzz106.pub/liveBlind/index.m3u8', duration=duration)
        #self.client.play('http://devimages.apple.com/iphone/samples/bipbop/bipbopall.m3u8', duration=duration)
        self.client.play('http://192.168.233.131/wp/website-67-0.com/vxoa/ch0/hls/index.m3u8', duration=duration)
        #self.client.play('http://172.25.0.9/vxoa/ch0/hls/index.m3u8', duration=duration)

class HLSUser(hlsplayer.HLSLocust):
    task_set = UserBehavior
    min_wait=  2*SECONDS # 2 seconds
    max_wait=  5*SECONDS # 5 seconds

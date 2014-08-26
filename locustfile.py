import random
from locust import TaskSet, task

import hlslocust.hlsplayer as hlsplayer

SECONDS = 1000

class UserBehavior(TaskSet):
    @task
    def play_random(self):
        duration = random.randint(60, 600) 
        i = random.randint(1, 20) 
        j = random.randint(1, 50) 
        self.client.play('http://172.25.46.12/wp/liveeve{i}.bench/lhls{j}/hls/playlist.m3u8'.format(i=i,j=j), 
                         duration=duration)

class HLSUser(hlsplayer.HLSLocust):
    task_set = UserBehavior
    min_wait = 2 * SECONDS # 2 seconds
    max_wait = 15 * SECONDS # 5 seconds

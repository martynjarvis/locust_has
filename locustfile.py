from locust import TaskSet, task

import hlslocust.hls as hls

class UserBehavior(TaskSet):
    @task()
    def play(self):
        self.client.play('http://testsite.zzz106.pub/liveBlind/index.m3u8', duration=600)

class HLSUser(hls.HLSLocust):
    task_set = UserBehavior
    min_wait=5000
    max_wait=9000

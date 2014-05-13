from locust import TaskSet, task

import hlslocust.hls as hls

class UserBehavior(TaskSet):
    @task()
    def play(self):
        self.client.play('http://localhost:8000/example/NTV-Public-IPS.m3u8')

class HLSUser(hls.HLSLocust):
    task_set = UserBehavior
    min_wait=5000
    max_wait=9000

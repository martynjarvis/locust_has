from locust import Locust, TaskSet, task
import hlslocust.hls as hls

class UserBehavior(TaskSet):
    @task()
    def play(self):
        self.client.play('http://localhost:8000/example/NTV-Public-IPS.m3u8')

class HLSLocust(Locust):
    def __init__(self, *args, **kwargs):
        super(HLSLocust, self).__init__(*args, **kwargs)
        self.client = hls.Player()

class WebsiteUser(HLSLocust):
    task_set = UserBehavior
    min_wait=5000
    max_wait=9000

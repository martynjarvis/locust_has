import unittest
import SimpleHTTPServer
import SocketServer
import threading
import time
from mock import patch, Mock
 
import hlslocust.hlsplayer as hlsplayer

# allow sockets to be reused when we rerun tests
SocketServer.TCPServer.allow_reuse_address = True

def side_effect():
    side_effect.fake_time+=0.2
    return side_effect.fake_time
side_effect.fake_time = time.time()

time_mock = Mock()
time_mock.side_effect = side_effect

class TddPlay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = WebServer()
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def setUp(self):
        self.hls_player = hlsplayer.Player()
        #self.server = WebServer()
        #self.server.start()

    #def tearDown(self):
        #self.server.stop()
        #time.sleep(1)

    @patch('time.time', new=time_mock)
    @patch('gevent.sleep', return_value=None)
    def test_live_play(self, patched_sleep):
        buffer_time, play_time = self.hls_player.play(url='http://localhost:8000/live-example/NTV-Public-IPS.m3u8', duration=22)
        self.assertEqual(buffer_time,24.0) # how long the plalists were
        self.assertGreaterEqual(play_time,22.0) # how long we took playing it before we returned
        self.assertLess(play_time,23.0) # how long we took playing it before we returned

    @patch('time.time', new=time_mock)
    @patch('gevent.sleep', return_value=None)
    def test_vod_play(self, patched_sleep):
        buffer_time, play_time = self.hls_player.play(url='http://localhost:8000/vod-example/index.m3u8')
        self.assertEqual(buffer_time,141.0) # how long the plalists were
        self.assertGreaterEqual(play_time,141.0) # how long we took playing it before we returned
        self.assertLess(play_time,142.0) # how long we took playing it before we returned

class WebServer(threading.Thread):
    def __init__(self):
        PORT = 8000
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        self.httpd = SocketServer.TCPServer(("", PORT), Handler)
        threading.Thread.__init__(self)

    def run(self):
        self.httpd.serve_forever()

    def stop(self):
        self.httpd.shutdown()

   

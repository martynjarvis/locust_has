import unittest
import SimpleHTTPServer
import SocketServer
import threading
from mock import patch, Mock
 
import hlslocust.hls as hls

# allow sockets to be reused when we rerun tests
SocketServer.TCPServer.allow_reuse_address = True

time_mock = Mock()
time_mock.side_effect = [(30.0*x/10) for x in range(0,10)]

class TddPlay(unittest.TestCase):
    def setUp(self):
        self.hls_player = hls.Player()
        self.server = WebServer()
        self.server.start()

    def tearDown(self):
        self.server.stop()

    #@patch('time.time', new=time_mock)
    @patch('gevent.sleep', return_value=None)
    def test_play(self, patched_sleep):
        buffer_time, play_time = self.hls_player.play(url='http://localhost:8000/example/NTV-Public-IPS.m3u8',duration=2)
        self.assertEqual(buffer_time,24.0) # how long the plalists were
        self.assertGreaterEqual(play_time,2.0) # how long we took playing it before we returned
        self.assertLess(play_time,2.5) # how long we took playing it before we returned

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

if __name__ == '__main__':
    unittest.main()
   

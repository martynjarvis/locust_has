import unittest
import ..hls

# examples
# index.m3u8  NTV-Public-IPS.m3u8  public_200.m3u8  public_400.m3u8


class TddMasterPlaylist(unittest.TestCase):
    def setUp(self):
        self.hls_player = hls.Player()
        with open('example/NTV-Public-IPS.m3u8') as f:
            self.hls_player.parse(f.read())

    def test_playlists(self):
        self.assertEqual(self.hls_player.playlists, 
            ['http://public.infozen.cshls.lldns.net/infozen/public/public/public_200.m3u8',
             'http://public.infozen.cshls.lldns.net/infozen/public/public/public_400.m3u8',
             'http://public.infozen.cshls.lldns.net/infozen/public/public/public_200.m3u8'])

class TddMediaPlaylist(unittest.TestCase):
    def setUp(self):
        self.hls_player = hls.Player()
        with open('example/public_200.m3u8') as f:
            self.hls_player.parse(f.read())

    def test_manifest_queue(self):
        filenames = [x.name for x in self.hls_player.queue]
        self.assertEqual(filenames,
                ['../../infozen_public/streams/public/public_200Num32458.ts',
                '../../infozen_public/streams/public/public_200Num32459.ts',
                '../../infozen_public/streams/public/public_200Num32460.ts',
                '../../infozen_public/streams/public/public_200Num32461.ts',
                '../../infozen_public/streams/public/public_200Num32462.ts',
                '../../infozen_public/streams/public/public_200Num32463.ts',
                '../../infozen_public/streams/public/public_200Num32464.ts',
                '../../infozen_public/streams/public/public_200Num32465.ts'])

    def test_manifest_durations(self):
        durations = [x.duration for x in self.hls_player.queue]
        self.assertEqual(durations, [3]*8)

    def test_attributes(self):
        self.assertEqual(self.hls_player.media_sequence, 32458)
        self.assertEqual(self.hls_player.allow_cache, False)
        self.assertEqual(self.hls_player.version, 2)
        self.assertEqual(self.hls_player.targetduration, 3)
                
if __name__ == '__main__':
    unittest.main()

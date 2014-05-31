import unittest
 
import hlslocust.hls as hls
import hlslocust.cast as cast

class TddSplitting(unittest.TestCase):
    def test_simple_split(self):
        self.assertEqual(list(cast.my_split('1,2,3,4')),
                         ['1','2','3','4'])
        self.assertEqual(list(cast.my_split('1,"2,3",4')),
                         ['1','"2,3"','4'])
        self.assertEqual(list(cast.my_split("1,'2,3',4")),
                         ['1',"'2,3'",'4'])
        self.assertEqual(list(cast.my_split("1,'2,3',4")),
                         ['1',"'2,3'",'4'])

    def test_complex_split(self):
        long_str = 'PROGRAM-ID=1,BANDWIDTH=602230,CODECS="avc1.66.31, mp4a.40.2",RESOLUTION=320x240'
        exp_res = ['PROGRAM-ID=1','BANDWIDTH=602230',
                   'CODECS="avc1.66.31, mp4a.40.2"','RESOLUTION=320x240']
        self.assertEqual(list(cast.my_split(long_str)),exp_res)

    def test_trailing_comma(self):
        self.assertEqual(list(cast.my_split('1,2,3,')), ['1','2','3'])
                
    def test_single_item(self):
        self.assertEqual(list(cast.my_split('test')), ['test'])

class TddCasting(unittest.TestCase):
    def test_castInt(self):
        self.assertEqual(cast.my_cast('1'),1)
        self.assertEqual(cast.my_cast('-1'),-1)

    def test_castFloat(self):
        self.assertEqual(cast.my_cast('1.5'),1.5)
        self.assertEqual(cast.my_cast('1.0'),1.0)
        self.assertEqual(cast.my_cast('-1.0'),-1.0)

    def test_castBool(self):
        self.assertEqual(cast.my_cast('NO'),False)
        self.assertEqual(cast.my_cast('No'),False)
        self.assertEqual(cast.my_cast('no'),False)
        self.assertEqual(cast.my_cast('YES'),True)
        self.assertEqual(cast.my_cast('Yes'),True)
        self.assertEqual(cast.my_cast('yes'),True)

    def test_castList(self):
        self.assertEqual(cast.my_cast('No,10,100.0'),[False,10,100.0])

    def test_castDict(self):
        self.assertEqual(cast.my_cast('PROGRAM-ID=1127167744,BANDWIDTH=1000000'),
                         {'program_id':1127167744,'bandwidth':1000000})

class TddMasterPlaylist(unittest.TestCase):
    def setUp(self):
        self.master_playlist = hls.MasterPlaylist('master','test.com/index')
        with open('example/NTV-Public-IPS.m3u8') as f:
            self.master_playlist.parse(f.read())

    def test_playlist_urls(self):
        playlists = [x.url for x in
                     self.master_playlist.media_playlists]
        self.assertEqual(playlists,
            ['test.com/public_1000.m3u8',
             'test.com/public_400.m3u8',
             'test.com/public_200.m3u8'])

    def test_playlist_names(self):
        playlists = [x.name for x in
                     self.master_playlist.media_playlists]
        self.assertEqual(playlists,
            ['public_1000.m3u8',
             'public_400.m3u8',
             'public_200.m3u8'])

    def test_playlist_bandwidths(self):
        bandwidths = [x.bandwidth for x in
                      self.master_playlist.media_playlists]
        self.assertEqual(bandwidths, [1000000, 400000, 200000])

    def test_playlist_id(self):
        program_ids = [x.program_id for x in
                       self.master_playlist.media_playlists]
        self.assertEqual(program_ids, [1127167744, 1127167744, 1127167744])

    def test_duplicate_playlists(self):
        with open('example/NTV-Public-IPS.m3u8') as f:
            self.master_playlist.parse(f.read())
        self.assertEqual(len(self.master_playlist.media_playlists),3)

class TddMediaPlaylist(unittest.TestCase):
    def setUp(self):
        self.media_playlist = hls.MediaPlaylist('test','test.com/test')
        with open('example/public_200.m3u8') as f:
            self.media_playlist.parse(f.read())

    def test_fragment_names(self):
        filenames = [x.name for x in self.media_playlist.media_fragments]
        self.assertEqual(filenames,
                ['public_200/Num32458.ts',
                 'public_200/Num32459.ts',
                 'public_200/Num32460.ts',
                 'public_200/Num32461.ts',
                 'public_200/Num32462.ts',
                 'public_200/Num32463.ts',
                 'public_200/Num32464.ts',
                 'public_200/Num32465.ts'])

    def test_fragment_urls(self):
        filenames = [x.url for x in self.media_playlist.media_fragments]
        self.assertEqual(filenames,
                ['test.com/public_200/Num32458.ts',
                 'test.com/public_200/Num32459.ts',
                 'test.com/public_200/Num32460.ts',
                 'test.com/public_200/Num32461.ts',
                 'test.com/public_200/Num32462.ts',
                 'test.com/public_200/Num32463.ts',
                 'test.com/public_200/Num32464.ts',
                 'test.com/public_200/Num32465.ts'])

    def test_fragment_durations(self):
        durations = [x.duration for x in self.media_playlist.media_fragments]
        self.assertEqual(durations, [3]*8)

    def test_media_playlist_attributes(self):
        self.assertEqual(self.media_playlist.media_sequence, 32458)
        self.assertEqual(self.media_playlist.allow_cache, False)
        self.assertEqual(self.media_playlist.version, 2)

    def test_duplicate_fragments(self):
        with open('example/public_200.m3u8') as f:
            self.media_playlist.parse(f.read())
        self.assertEqual(len(self.media_playlist.media_fragments),8)

if __name__ == '__main__':
    unittest.main()
   

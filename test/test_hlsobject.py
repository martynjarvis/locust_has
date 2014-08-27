import unittest
 
import hlslocust.hlsobject as hlsobject

class TddMasterPlaylist(unittest.TestCase):
    def setUp(self):
        self.master_playlist = hlsobject.MasterPlaylist('master','test.com/index')
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
        self.media_playlist = hlsobject.MediaPlaylist('test','test.com/test')
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

    def test_fragment_sequence(self):
        filenames = [x.media_sequence for x in self.media_playlist.media_fragments]
        self.assertEqual(filenames, [32458, 32459, 32460, 32461, 32462, 32463,
                                     32464, 32465])

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
        self.assertEqual(self.media_playlist.allow_cache, False)
        self.assertEqual(self.media_playlist.version, 2)
        self.assertEqual(self.media_playlist.targetduration, 3)
        self.assertEqual(self.media_playlist.endlist, True)
        self.assertEqual(self.media_playlist.media_sequence, 32458)

    def test_media_sequence(self):
        self.assertEqual(self.media_playlist.first_media_sequence(), 32458)
        self.assertEqual(self.media_playlist.last_media_sequence(), 32465)
        self.assertEqual(self.media_playlist.get_media_fragment(32460).media_sequence, 32460)

    def test_duplicate_fragments(self):
        with open('example/public_200.m3u8') as f:
            self.media_playlist.parse(f.read())
        self.assertEqual(len(self.media_playlist.media_fragments),8)

   

import unittest
 
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
    def test_cast_int(self):
        self.assertEqual(cast.my_cast('1'),1)
        self.assertEqual(cast.my_cast('-1'),-1)

    def test_cast_float(self):
        self.assertEqual(cast.my_cast('1.5'),1.5)
        self.assertEqual(cast.my_cast('1.0'),1.0)
        self.assertEqual(cast.my_cast('-1.0'),-1.0)

    def test_cast_bool(self):
        self.assertEqual(cast.my_cast('NO'), False)
        self.assertEqual(cast.my_cast('No'), False)
        self.assertEqual(cast.my_cast('no'), False)
        self.assertEqual(cast.my_cast('YES'), True)
        self.assertEqual(cast.my_cast('Yes'), True)
        self.assertEqual(cast.my_cast('yes'), True)

    def test_cast_list(self):
        self.assertEqual(cast.my_cast('No,10,100.0'),[False,10,100.0])

    def test_single_item_list(self):
        self.assertEqual(cast.my_cast('9.9,'), [9.9])
        self.assertEqual(cast.my_cast('10,'), [10])

    def test_cast_dict(self):
        self.assertEqual(cast.my_cast('PROGRAM-ID=1127167744,BANDWIDTH=1000000'),
                         {'program_id':1127167744,'bandwidth':1000000})


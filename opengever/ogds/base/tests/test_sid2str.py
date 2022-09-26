from opengever.ogds.base.sync.sid2str import sid2str
import unittest


class Sid2StrTestCase(unittest.TestCase):

    def test_sid2str(self):
        sid = ('\x01\x05\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00\\\xc6\xb6}'
               '\xa8\x02\xb59\x0f/\xf59\x125\x00\x00')
        self.assertEqual(
            sid2str(sid), 'S-1-5-21-2109130332-968164008-972369679-13586')

    def test_sid2str_with_invalid_sid(self):
        sid = 'foo'
        self.assertEqual(sid2str(sid), '')
        sid = '\x01\x05\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00\\\xc6\xb6'
        self.assertEqual(sid2str(sid), '')

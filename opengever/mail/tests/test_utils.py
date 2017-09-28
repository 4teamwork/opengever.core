from email.header import decode_header
from opengever.mail.utils import make_addr_header
import unittest


class TestMakeAddrHeader(unittest.TestCase):

    def test_encodes_addr_name(self):
        fullname = u'Fr\xe4nzi M\xfcller'
        address = 'fraenzi.mueller@example.org'
        header = make_addr_header(fullname, address)
        self.assertEquals(
            [('Fr\xc3\xa4nzi M\xc3\xbcller', 'utf-8'),
             ('<fraenzi.mueller@example.org>', None)],
            decode_header(header))

    def test_preserves_addr_spec(self):
        fullname = u'Fr\xe4nzi M\xfcller'
        address = 'fraenzi.mueller@example.org'
        header = make_addr_header(fullname, address)
        self.assertIn(' <fraenzi.mueller@example.org>', str(header))

    def test_preserves_bails_on_bytestring_names(self):
        fullname = 'bytestring'
        address = ''
        with self.assertRaises(ValueError):
            make_addr_header(fullname, address)

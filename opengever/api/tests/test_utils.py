from opengever.api.utils import recursive_encode
import unittest


class TestRecursiveEncode(unittest.TestCase):
    """
    """

    def equals(self, input, output):
        self.assertEqual(recursive_encode(input), output)

    def test_unicode(self):
        self.equals(u'foo', 'foo')
        self.equals(u'b\xe4r', 'b\xc3\xa4r')
        self.equals('b\xc3\xa4r', 'b\xc3\xa4r')

    def test_dicts(self):
        self.equals({u'b\xe4r': u'b\xe4r'},
                    {'b\xc3\xa4r': 'b\xc3\xa4r'})

    def test_lists(self):
        self.equals([u'b\xe4r'], ['b\xc3\xa4r'])

    def test_other_types(self):
        self.equals([1, 2.2, True, False, None],
                    [1, 2.2, True, False, None])

        self.equals(1, 1)
        self.equals(None, None)

    def test_nesting(self):
        input = {
            u'b\xe4r': {
                u'b\xe4r': [
                    u'b\xe4r',
                    1,
                    True]},
            'blubb': [{u'b\xe4r': 3}]}

        output = {
            'b\xc3\xa4r': {
                'b\xc3\xa4r': [
                    'b\xc3\xa4r',
                    1,
                    True]},
            'blubb': [{'b\xc3\xa4r': 3}]}

        self.equals(input, output)

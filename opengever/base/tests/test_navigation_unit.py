from opengever.base.browser.navigation import make_tree_by_url
from unittest2 import TestCase
import json


class TestMakeTreeByUrl(TestCase):

    def test(self):
        input = [{'url': '/one/two/three/four'},
                 {'url': '/one/two'},
                 {'url': '/one/two/three'},
                 {'url': '/one/two/copy-of-three'}]

        expected = [
            {'url': '/one/two',
             'nodes': [
                    {'url': '/one/two/three',
                     'nodes': [
                            {'url': '/one/two/three/four',
                             'nodes': []}]},
                    {'url': '/one/two/copy-of-three',
                     'nodes': []}]}]

        self.assert_json_equal(expected, make_tree_by_url(input))

    def assert_json_equal(self, expected, got, msg=None):

        pretty = {'sort_keys': True, 'indent': 4, 'separators': (',', ': ')}
        expected_json = json.dumps(list(expected), **pretty)
        got_json = json.dumps(list(got), **pretty)
        self.maxDiff = None
        self.assertMultiLineEqual(expected_json, got_json, msg)

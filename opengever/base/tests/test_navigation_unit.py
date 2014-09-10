from opengever.base.browser.navigation import make_tree_by_path
from unittest2 import TestCase
import json


class TestMakeTreeByPath(TestCase):

    def test(self):
        input = [{'path': '/one/two/three/four'},
                 {'path': '/one/two'},
                 {'path': '/one/two/three'},
                 {'path': '/one/two/copy-of-three'}]

        expected = [
            {'path': '/one/two',
             'nodes': [
                    {'path': '/one/two/three',
                     'nodes': [
                            {'path': '/one/two/three/four',
                             'nodes': []}]},
                    {'path': '/one/two/copy-of-three',
                     'nodes': []}]}]

        self.assert_json_equal(expected, make_tree_by_path(input))

    def assert_json_equal(self, expected, got, msg=None):

        pretty = {'sort_keys': True, 'indent': 4, 'separators': (',', ': ')}
        expected_json = json.dumps(list(expected), **pretty)
        got_json = json.dumps(list(got), **pretty)
        self.maxDiff = None
        self.assertMultiLineEqual(expected_json, got_json, msg)

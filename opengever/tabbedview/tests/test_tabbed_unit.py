from opengever.tabbedview import GeverTabbedView
from unittest2 import TestCase


class SimpleTabDefs(GeverTabbedView):

    def _get_tabs(self):
        return [{
            'id': 'foo',
            'title': 'Foo!',
        }]


class ExtensiveTabDefs(GeverTabbedView):

    def _get_tabs(self):
        return [{
            'id': 'foo',
            'title': 'Foo!',
            'url': 'http://example.com',
        }]


class TestUnitGeverTabbedView(TestCase):

    def test_prefills_defaults(self):
        self.assertEqual([{
                'id': 'foo',
                'title': 'Foo!',
                'icon': None,
                'url': '#',
                'class': None,
            }],
            SimpleTabDefs(None, None).get_tabs())

    def test_preserves_overridden_defaults(self):
        self.assertEqual([{
                'id': 'foo',
                'title': 'Foo!',
                'url': 'http://example.com',
                'icon': None,
                'class': None,
            }],
            ExtensiveTabDefs(None, None).get_tabs())

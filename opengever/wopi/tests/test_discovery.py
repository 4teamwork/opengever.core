from contextlib import contextmanager
from ftw.testing import MockTestCase
from lxml import etree
from mock import Mock
from opengever.wopi import discovery
from opengever.wopi.discovery import actions_by_extension
from opengever.wopi.discovery import editable_extensions
from opengever.wopi.discovery import etree_to_dict
from plone.registry.interfaces import IRegistry
import os.path
import requests_mock


class MockRegistry:
    def forInterface(self, interface):
        records = Mock()
        records.get.return_value = 'https://officeonline/hosting/discovery'
        return records

    def __getitem__(self, key):
        return 'https://officeonline/hosting/discovery'


class TestWOPIDiscovery(MockTestCase):

    def test_etree_to_dict(self):
        xml = '<a><b>text</b><b>more text</b><c attr="value">foo<d/></c></a>'
        et = etree.fromstring(xml)
        self.assertEqual(
            etree_to_dict(et),
            {
                'a': {
                    'b': ['text', 'more text'],
                    'c': {
                        '#text': 'foo',
                        '@attr': 'value',
                        'd': None
                    },
                },
            }
        )

    @contextmanager
    def mock_discovery_request(self):
        self.mock_utility(MockRegistry(), IRegistry)
        with open(
            os.path.join(os.path.dirname(__file__), 'data',
                         'discovery_xml.txt')
        ) as data_file:
            resp = data_file.read()
        with requests_mock.mock() as mock:
            mock.get(
                'https://officeonline/hosting/discovery',
                text=resp)
            yield mock

    def test_actions_by_extension(self):
        with self.mock_discovery_request():
            actions = actions_by_extension()

        self.assertIn('docx', actions)
        self.assertIn('edit', actions['docx'])
        self.assertIn('urlsrc', actions['docx']['edit'])

    def test_actions_by_extension_gets_cached(self):
        discovery._ACTIONS = {}
        with self.mock_discovery_request() as mock:
            actions_by_extension()
            actions_by_extension()

        self.assertEqual(mock.call_count, 1)

    def test_editable_extensions(self):
        with self.mock_discovery_request():
            extensions = editable_extensions()

        self.assertEqual(
            extensions,
            set(
                [
                    "wopitestx",
                    "pptx",
                    "docx",
                    "xlsb",
                    "ppsx",
                    "xlsx",
                    "odp",
                    "ods",
                    "odt",
                    "one",
                    "wopitest",
                    "xlsm",
                    "docm",
                    "vsdx",
                    "onetoc2",
                ]
            ),
        )

    def test_editable_extansions_gets_cached(self):
        discovery._EDITABLE_EXTENSIONS = {}
        discovery._ACTIONS = {}
        with self.mock_discovery_request() as mock:
            editable_extensions()
            discovery._ACTIONS = {}
            editable_extensions()

        self.assertEqual(mock.call_count, 1)

from contextlib import contextmanager
from ftw.testing import MockTestCase
from lxml import etree
from mock import Mock
from opengever.wopi import discovery
from opengever.wopi.discovery import actions_by_extension
from opengever.wopi.discovery import editable_extensions
from opengever.wopi.discovery import etree_to_dict
from opengever.wopi.discovery import run_discovery
from plone.registry.interfaces import IRegistry
from requests.exceptions import ConnectTimeout
import os.path
import requests_mock
import time


class MockRegistry:
    def forInterface(self, interface, check=True, omit=(), prefix=None):
        records = Mock()
        records.get.return_value = 'https://officeonline/hosting/discovery'
        return records

    def __getitem__(self, key):
        return 'https://officeonline/hosting/discovery'


class TestWOPIDiscovery(MockTestCase):

    def setUp(self):
        super(TestWOPIDiscovery, self).setUp()
        discovery._WOPI_DISCOVERY['timestamp'] = 0
        self.mock_utility(MockRegistry(), IRegistry)

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
    def mock_discovery_request(self, response_file='discovery_xml.txt'):
        with open(
            os.path.join(os.path.dirname(__file__), 'data', response_file)
        ) as data_file:
            resp = data_file.read()
        with requests_mock.mock() as mock:
            mock.get(
                'https://officeonline/hosting/discovery',
                text=resp)
            yield mock

    @contextmanager
    def mock_failing_discovery_request(self):
        with requests_mock.mock() as mock:
            mock.get(
                'https://officeonline/hosting/discovery',
                exc=ConnectTimeout)
            yield mock

    def test_actions_by_extension(self):
        with self.mock_discovery_request():
            actions = actions_by_extension()

        self.assertIn('docx', actions)
        self.assertIn('edit', actions['docx'])
        self.assertIn('urlsrc', actions['docx']['edit'])

    def test_actions_by_extension_gets_cached(self):
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

    def test_editable_extensions_returns_empty_list_if_discovery_is_not_successfull(self):
        with self.mock_discovery_request(response_file='discovery_without_actions_xml.txt'):
            extensions = editable_extensions()

        self.assertEqual(extensions, set([]))

    def test_editable_extansions_gets_cached(self):
        with self.mock_discovery_request() as mock:
            editable_extensions()
            editable_extensions()

        self.assertEqual(mock.call_count, 1)

    def test_proof_key(self):
        with self.mock_discovery_request():
            proof_key = discovery.proof_key()
        self.assertEqual(
            proof_key,
            {
                '@exponent': 'AQAB',
                '@modulus': '2ZmWOemDkf8agcFq4F66CcJL3MyccIjnAvcqFPjGtv6fPwsCO'
                'adpt2E9NMB3VAPj786PqMaWe038hzJ6TF3WlCEK0opWQIBNbSzcDM3arM3nkO'
                'mg3mQWE15zIU1IIdm9M8UIhCLAUd1w34HVGOnp+L2TBLl+Knx8I9URt9lwVcl'
                'mcNxUEJ+IG+3aG0aP5CP71toW9Ctv8cMybu7ci6cfOzj45cWnhVd0QOR0m1MI'
                'yfDsYss1GVYrvh7K0ExJR9LrDr6lHDPxBHixDSwnUtTj/m832JdljbZqhTnfC'
                'p7IkYm5b3r4DbFStR9n56qojZ5uIKhGQzvjxvvusTYYmBxoLQ==',
                '@oldexponent': 'AQAB',
                '@oldmodulus': 'pGkeSFBe6g6cuetNOOeEZNPX61f9IpOxXnl4VzkSHSEAs9'
                'a4xa9nxKhZoT9X1aavNwOkyagflB92es2gLapT2LhAKcbrPm4mmjPTLp+2h3K'
                '6dqA/8mvBOZdxWoD7F0RyR06k/d7YcJHX6iEX0UnP6OBhz57ZdmM9g7BvSoR1'
                'OGMiZQw/abqEj//NljnvNg/35vCcoVYCI6ghQhm3/yPCm1o71JA+E+oq1Ayrw'
                'aKPKQLyZj6rB1Lzr/sFcjpv6lrwJEeZFti8YqjyMAYBZoWqvnDGzCLiiTzdJ7'
                'z1P33DpOLvaSteORdeZ7adhCAvEMOex+v8VqsawIvLwVt+TosoPQ==',
                '@oldvalue': 'BgIAAACkAABSU0ExAAgAAAEAAQA9KItOflvBy4vAGqtW/OvH'
                'nsMQLyCEnbZnXhc5Xitp7+Kkw30/9bwn3TyJ4iLMxnC+qoVmAQYw8qhivNgWm'
                'Uck8FrqbzpyBfuv81IHqz5m8gIpj6LBqwzUKuoTPpDUO1qbwiP/txlCIagjAl'
                'ahnPDm9w827zmWzf+PhLppPwxlImM4dYRKb7CDPWN22Z7PYeDoz0nRFyHq15F'
                'w2N79pE5HckQX+4BacZc5wWvyP6B2unKHtp8u0zOaJm4+68YpQLjYU6otoM16'
                'dh+UH6jJpAM3r6bVVz+hWajEZ6/FuNazACEdEjlXeHlesZMi/Vfr19NkhOc4T'
                'eu5nA7qXlBIHmmk',
                '@value': 'BgIAAACkAABSU0ExAAgAAAEAAQAtaByYGDax7vvG4ztDRqggbp6'
                'NqKrnZx+1UrEN+HpvuYmRyJ4K3zmFaraNZZfYN2/+49RSJywNsXgE8TMcpb4O'
                '69JHSUzQyh6+K1YZNcti7PDJCFObdORAdFeFp8Xl+Dg7H6eL3O5uMsPxbyv0F'
                'trW+yPkj0Yb2u0biJ8QVNxwZslVcNm3EdUjfHwqfrkEk7346ekY1YHfcN1RwC'
                'KECMUzvdkhSE0hc14TFmTeoOmQ582s2s0M3CxtTYBAVorSCiGU1l1MejKH/E1'
                '7lsaoj87v4wNUd8A0PWG3aac5Ags/n/62xvgUKvcC54hwnMzcS8IJul7gasGB'
                'Gv+Rg+k5lpnZ',
            },
        )

    def test_fetches_again_after_refresh_interval(self):
        with self.mock_discovery_request() as mock:
            discovery.proof_key()
            discovery._WOPI_DISCOVERY['timestamp'] = (
                int(time.time()) - discovery.WOPI_DISCOVERY_REFRESH_INTERVAL - 1
            )
            discovery.proof_key()

        self.assertEqual(mock.call_count, 2)

    def test_run_discovery_is_robust_regarding_network_failures(self):
        with self.mock_failing_discovery_request():
            result = run_discovery()

        self.assertIsNone(result)

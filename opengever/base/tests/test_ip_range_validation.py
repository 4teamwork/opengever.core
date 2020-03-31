from ipaddress import ip_network
from opengever.base.ip_range import InvalidIPRangeSpecification
from opengever.base.ip_range import parse_ip_range
from opengever.base.ip_range import permitted_ip
from opengever.base.ip_range import valid_ip_range
from zope.interface import Invalid
import unittest


class TestIPRangeParsing(unittest.TestCase):

    def test_single_ipv4_address_is_parsed(self):
        self.assertEqual(
            [ip_network(u'192.168.0.1')],
            parse_ip_range('192.168.0.1'))

    def test_single_ipv4_cidr_network_is_parsed(self):
        self.assertEqual(
            [ip_network(u'192.168.0.0/16')],
            parse_ip_range('192.168.0.0/16'))

    def test_invalid_ip_address_raises_exception(self):
        with self.assertRaises(InvalidIPRangeSpecification):
            parse_ip_range('500.500.0.0')

    def test_multiple_ipv4_addresses_are_parsed(self):
        self.assertEqual(
            [ip_network(u'10.0.0.1'), ip_network(u'192.168.0.1')],
            parse_ip_range('10.0.0.1,192.168.0.1'))

    def test_mix_of_single_adress_and_networks_is_parsed(self):
        self.assertEqual(
            [ip_network(u'10.1.1.5'), ip_network(u'192.168.0.0/16')],
            parse_ip_range('10.1.1.5,192.168.0.0/16'))

    def test_white_space_is_stripped(self):
        self.assertEqual(
            [ip_network(u'10.0.0.1'), ip_network(u'192.168.0.1')],
            parse_ip_range('10.0.0.1  ,  192.168.0.1'))


class TestPermittedIPChecking(unittest.TestCase):

    def test_allowed_ip_in_single_ipv4_address_range(self):
        self.assertTrue(
            permitted_ip('192.168.0.1', '192.168.0.1')
        )

    def test_disallowed_ip_in_single_ipv4_address_range(self):
        self.assertFalse(
            permitted_ip('10.0.0.0', '192.168.0.1')
        )

    def test_allowed_ip_in_single_ipv4_cidr_network_range(self):
        self.assertTrue(
            permitted_ip('192.168.0.1', '192.168.0.0/16')
        )

    def test_disallowed_ip_in_single_ipv4_cidr_network_range(self):
        self.assertFalse(
            permitted_ip('10.0.0.0', '192.168.0.0/16')
        )

    def test_invalid_ip_address_is_rejected(self):
        with self.assertRaises(ValueError):
            permitted_ip('500.500.0.0', '192.168.0.0/16')

    def test_invalid_ip_range_is_rejected(self):
        self.assertFalse(
            permitted_ip('10.0.0.1', '500.500.0.0/33')
        )

    def test_allowed_ip_in_multiple_ipv4_address_ranges(self):
        self.assertTrue(
            permitted_ip('10.0.0.5', '10.0.0.5, 192.168.0.1')
        )
        self.assertTrue(
            permitted_ip('192.168.0.1', '10.0.0.5, 192.168.0.1')
        )

    def test_disallowed_ip_in_multiple_ipv4_address_ranges(self):
        self.assertFalse(
            permitted_ip('192.168.0.7', '10.0.0.5, 192.168.0.1')
        )

    def test_allowed_ip_in_multiple_ipv4_cidr_network_ranges(self):
        self.assertTrue(
            permitted_ip('192.168.5.5', '10.0.0.0/8, 192.168.0.0/16')
        )
        self.assertTrue(
            permitted_ip('10.1.5.20', '10.0.0.0/8, 192.168.0.0/16')
        )


class TestIPRangeFormValidator(unittest.TestCase):

    def test_single_ipv4_address_is_valid(self):
        self.assertTrue(valid_ip_range('192.168.0.1'))

    def test_single_ipv4_cidr_network_is_valid(self):
        self.assertTrue(valid_ip_range('192.168.0.0/16'))

    def test_invalid_ip_range_is_rejected(self):
        with self.assertRaises(Invalid):
            valid_ip_range('500.500.0.0/33')

    def test_multiple_ipv4_addresses_are_valid(self):
        self.assertTrue(valid_ip_range('10.0.0.1, 192.168.0.1'))

    def test_multiple_ipv4_cidr_networks_are_valid(self):
        self.assertTrue(valid_ip_range('10.0.0.0/8, 192.168.0.0/16'))

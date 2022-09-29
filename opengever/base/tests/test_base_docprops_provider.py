from opengever.base.docprops import BaseDocPropertyProvider
import unittest


class SampleProvider(BaseDocPropertyProvider):

    def _collect_properties(self):
        return {
            'foo': 42,
            'bar': 'Hello',
        }


class TestBaseDocPropertyProvider(unittest.TestCase):

    def setUp(self):
        self.provider = SampleProvider(context=None)

    def test_get_properties_prefixes_with_app_by_default(self):
        actual = self.provider.get_properties()
        expected = {
            'ogg.foo': 42,
            'ogg.bar': 'Hello',
        }
        self.assertEqual(expected, actual)

    def test_get_properties_supports_custom_prefix(self):
        actual = self.provider.get_properties(prefix='my_scope')
        expected = {
            'ogg.my_scope.foo': 42,
            'ogg.my_scope.bar': 'Hello',
        }
        self.assertEqual(expected, actual)

    def test_get_properties_supports_default_prefix(self):
        provider = SampleProvider(context=None)
        provider.DEFAULT_PREFIX = ('default_prefix', )

        actual = provider.get_properties()
        expected = {
            'ogg.default_prefix.foo': 42,
            'ogg.default_prefix.bar': 'Hello',
        }
        self.assertEqual(expected, actual)

        actual = provider.get_properties(prefix='my_scope')
        expected = {
            'ogg.my_scope.default_prefix.foo': 42,
            'ogg.my_scope.default_prefix.bar': 'Hello',
        }
        self.assertEqual(expected, actual)

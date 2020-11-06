from opengever.base.colorization import get_color
from opengever.testing import TestCase
import os


class TestGeverColorization(TestCase):

    def test_no_color_set(self):
        if 'GEVER_COLORIZATION' in os.environ:
            # Remove GEVER_COLORIZATION in case it is already defined
            os.environ.pop('GEVER_COLORIZATION')
        self.assertEqual(get_color(), None)

    def test_pre_configured_color(self):
        os.environ['GEVER_COLORIZATION'] = 'yellow'
        self.assertEqual(get_color(), '#EBD21E')

    def test_not_configured_color(self):
        os.environ['GEVER_COLORIZATION'] = 'Magenta'
        self.assertEqual(get_color(), 'Magenta')

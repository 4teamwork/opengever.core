import os
import unittest
import doctest
from Testing import ZopeTestCase as ztc
from opengever.mail.tests.base import MailTestCase


OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF)


HERE = os.path.dirname(os.path.abspath(__file__))


def test_suite():
    txtfiles = [f for f in os.listdir(HERE)
                if f.endswith('.txt') and
                not f.startswith('.')]

    return unittest.TestSuite([ztc.FunctionalDocFileSuite(
                    'tests/%s' % f, package='opengever.mail',
                    test_class=MailTestCase)
                 for f in txtfiles])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

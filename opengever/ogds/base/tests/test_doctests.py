from opengever.testing import OPENGEVER_INTEGRATION_TESTING
from plone.testing import layered
import doctest
import unittest2 as unittest


OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE |
               doctest.ELLIPSIS |
               doctest.REPORT_NDIFF)


TESTFILES = (
    'user_model.txt',
    'client_model.txt',
    'vocabularies.txt',
    'transport.txt',
    'autocomplete_widget.txt',
    'plugins.txt',
    )


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([layered(doctest.DocFileSuite(filename,
                                                 optionflags=OPTIONFLAGS),
                    layer=OPENGEVER_INTEGRATION_TESTING)
                    for filename in TESTFILES])
    return suite

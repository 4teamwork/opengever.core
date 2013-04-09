from Products.CMFCore.utils import getToolByName
from opengever.document.testing import OPENGEVER_DOCUMENT_FUNCTIONAL_TESTING
from plone.dexterity.utils import createContentInContainer
from zope.annotation.interfaces import IAnnotations
import datetime
import unittest2 as unittest
from plone.namedfile.file import NamedBlobFile


class TestDocumentIntegration(unittest.TestCase):

    layer = OPENGEVER_DOCUMENT_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.mock_file = NamedBlobFile('bla bla', filename=u'T\xf6st.txt')

    def test_title_from_filename(self):
        self.portal.invokeFactory('opengever.document.document', 'document1', file=self.mock_file)
        doc = self.portal.get('document1')
        self.assertEqual(doc.title, u'T\xf6st')
        self.assertEqual(doc.file.filename, u'tost.txt')
    
    def test_filename_from_title(self):
        self.portal.invokeFactory('opengever.document.document', 'document1', title="My Title", file=self.mock_file)
        doc = self.portal.get('document1')
        self.assertEqual(doc.title, u'My Title')
        self.assertEqual(doc.file.filename, u'my-title.txt')
        
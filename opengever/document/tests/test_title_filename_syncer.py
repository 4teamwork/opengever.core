from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.namedfile.file import NamedBlobFile


class TestTitleFilenameSyncer(FunctionalTestCase):

    def setUp(self):
        super(TestTitleFilenameSyncer, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.mock_file = NamedBlobFile('bla bla', filename=u'T\xf6st.txt')

    def test_title_from_filename(self):
        self.portal.invokeFactory(
            'opengever.document.document', 'document1', file=self.mock_file)
        doc = self.portal.get('document1')
        self.assertEqual(doc.title, u'T\xf6st')
        self.assertEqual(doc.file.filename, u'tost.txt')

    def test_filename_from_title(self):
        self.portal.invokeFactory(
            'opengever.document.document',
            'document1',
            title="My Title",
            file=self.mock_file)
        doc = self.portal.get('document1')
        self.assertEqual(doc.title, u'My Title')
        self.assertEqual(doc.file.filename, u'my-title.txt')

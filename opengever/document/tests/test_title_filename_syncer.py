from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase


class TestTitleFilenameSyncer(FunctionalTestCase):

    def test_infer_title_from_filename(self):
        document = create(Builder("document")
                          .attach_file_containing(u"blup", name=u'T\xf6st.txt'))
        self.assertEqual(document.title, u'T\xf6st')
        self.assertEqual(document.file.filename, u'tost.txt')

    def test_infer_filename_from_title(self):
        document = create(Builder("document")
                          .titled("My Title") \
                          .attach_file_containing(u"blup", name=u"wrong.txt"))
        self.assertEqual(document.title, u'My Title')
        self.assertEqual(document.file.filename, u'my-title.txt')

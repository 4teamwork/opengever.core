from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


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

    def test_filename_is_unicode(self):
        document = create(Builder("document")
                          .attach_file_containing(u"12", name=u"hmm.txt"))
        # set non-unicode title bypassing schema checks
        document.title = 'Ohh'
        notify(ObjectModifiedEvent(document))

        self.assertEqual(document.file.filename, u'ohh.txt')

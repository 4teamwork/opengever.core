from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
import os


class TestTitleFilenameSyncer(FunctionalTestCase):

    max_filename_length = 100

    def test_infer_title_from_filename(self):
        document = create(Builder("document")
                          .without_default_title()
                          .attach_file_containing(u"blup", name=u'T\xf6st.txt'))
        self.assertEqual(u'T\xf6st', document.title)
        self.assertEqual(u'Toest.txt', document.file.filename)

    def test_infer_filename_from_title(self):
        document = create(Builder("document")
                          .titled("My Title") \
                          .attach_file_containing(u"blup", name=u"wrong.txt"))
        self.assertEqual(u'My Title', document.title)
        self.assertEqual(u'My Title.txt', document.file.filename)

    def test_filename_is_unicode(self):
        document = create(Builder("document")
                          .attach_file_containing(u"12", name=u"hmm.txt"))
        # set non-unicode title bypassing schema checks
        document.title = 'Ohh'
        notify(ObjectModifiedEvent(document))

        self.assertEqual(u'Ohh.txt', document.file.filename)

    def test_filename_maximum_length_from_title(self):
        title = u''.join('a' for i in range(2*self.max_filename_length))
        expected_filename = title[:self.max_filename_length]+'.txt'

        document = create(Builder("document")
                          .titled(title)
                          .attach_file_containing(u"12", name=u"hmm.txt"))
        self.assertEqual(title, document.title)
        self.assertEqual(expected_filename, document.file.filename)

    def test_filename_maximum_length_from_filename(self):
        filename = u''.join('a' for i in range(2*self.max_filename_length))+'.txt'
        expected_title = os.path.splitext(filename)[0]
        expected_filename = expected_title[:self.max_filename_length]+'.txt'

        document = create(Builder("document")
                          .without_default_title()
                          .attach_file_containing(u"12", name=filename))
        self.assertEqual(expected_title, document.title)
        self.assertEqual(expected_filename, document.file.filename)

    def test_filename_maximum_length_respected_by_umlaut_transform(self):
        title = u''.join(u'\xe4' for i in range(2*self.max_filename_length))
        expected_filename = title.replace(u'\xe4', 'ae')[:self.max_filename_length]+'.txt'

        document = create(Builder("document")
                          .titled(title)
                          .attach_file_containing(u"12", name=u"hmm.txt"))
        self.assertEqual(title, document.title)
        self.assertEqual(expected_filename, document.file.filename)

    def test_filename_transform_from_title(self):
        """ Test that the filename transform preserves spaces and case,
        transforms umlauts and replaces dangerous special characters.
        """
        title = u'\xe4\xd6\xe9 / \\ . *'
        expected_filename = "aeOee ..txt"
        document = create(Builder("document")
                          .titled(title)
                          .attach_file_containing(u"12", name=u"hmm.txt"))

        self.assertEqual(title, document.title)
        self.assertEqual(expected_filename, document.file.filename)

    def test_filename_transform_from_filename(self):
        """ Test that the filename transform preserves spaces and case,
        transforms umlauts and replaces dangerous special characters.
        """
        filename = u'\xe4\xd6\xe9 / \\ . *.txt'
        expected_title = os.path.splitext(filename)[0]
        expected_filename = "aeOee ..txt"
        document = create(Builder("document")
                          .without_default_title()
                          .attach_file_containing(u"12", name=filename))

        self.assertEqual(expected_title, document.title)
        self.assertEqual(expected_filename, document.file.filename)

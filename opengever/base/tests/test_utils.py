from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import MockTestCase
from mocker import ANY
from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.base.utils import escape_html
from opengever.base.utils import file_checksum
from opengever.dossier.utils import find_parent_dossier
from opengever.testing import IntegrationTestCase
from plone.namedfile.file import NamedFile
from unittest import TestCase
from urllib import quote
import os.path


class TestAttachmentContentDisposition(MockTestCase):

    def setUp(self):
        super(TestAttachmentContentDisposition, self).setUp()
        self.header = []

        self.request = self.mocker.proxy({}, count=False)
        self.expect(
            self.request.response.setHeader(ANY, ANY)).call(
                lambda x, y: self.header.append(y)).count(0, None)

    def test_set_empty_filename(self):

        self.request['HTTP_USER_AGENT'] = ''

        self.replay()

        set_attachment_content_disposition(self.request, '')

        self.assertEqual(len(self.header), 0)

    def test_set_ms_filename(self):
        """ In Ms we must remove the quotes.
        """

        self.expect(self.request.get('HTTP_USER_AGENT', ANY)).result('MSIE')

        self.replay()

        set_attachment_content_disposition(self.request, 'MS Name')

        self.assertEquals(
            self.header[0],
            'attachment; filename=%s' % quote('MS Name'))

    def test_filename(self):
        """ Normaly we have the filename in quotes
        """

        self.expect(self.request.get('HTTP_USER_AGENT', ANY)).result('DEF')

        self.replay()

        set_attachment_content_disposition(self.request, 'Default Name')

        self.assertEquals(
            self.header[0],
            'attachment; filename="%s"' % 'Default Name')

    def test_with_file(self):
        self.expect(self.request.get('HTTP_USER_AGENT', ANY)).result('DEF')

        monk_file = NamedFile('bla bla', filename=u'test.txt')

        self.replay()

        set_attachment_content_disposition(
            self.request, 'Default Name', file=monk_file)

        self.assertEquals(
            self.header,
            ['text/plain', 7, 'attachment; filename="Default Name"'])


class TestFindParentDossier(IntegrationTestCase):

    def test_find_parent_dossier(self):
        self.login(self.regular_user)

        self.assertEquals(self.dossier, find_parent_dossier(self.document))

    def test_find_parent_inbox(self):
        self.login(self.secretariat_user)

        self.assertEquals(self.inbox, find_parent_dossier(self.inbox_document))

    def test_find_parent_on_nested_dossiers(self):
        self.login(self.regular_user)

        self.assertEquals(self.subdossier, find_parent_dossier(self.subdocument))

    def test_find_first_parent_dossier(self):
        self.login(self.regular_user)

        self.assertEquals(self.dossier, find_parent_dossier(self.taskdocument))

    def test_return_itself_if_dossier_is_passed(self):
        self.login(self.regular_user)

        self.assertEquals(self.dossier, find_parent_dossier(self.dossier))

    def test_raise_valuerror_if_plone_root_is_passed(self):
        self.login(self.regular_user)

        with self.assertRaises(ValueError):
            find_parent_dossier(self.portal)

    def test_raise_valuerror_if_plone_root_is_reached(self):
        self.login(self.regular_user)

        document = create(Builder('document'))
        with self.assertRaises(ValueError):
            find_parent_dossier(self.leaf_repofolder)


class TestEscapeHTML(TestCase):

    def test_escapes_lt_and_gt(self):
        text = 'Foo <Bar> Baz'
        self.assertEquals('Foo &lt;Bar&gt; Baz', escape_html(text))

    def test_escapes_double_quotes(self):
        text = 'Foo "Bar" Baz'
        self.assertEquals('Foo &quot;Bar&quot; Baz', escape_html(text))

    def test_escapes_apostrophes(self):
        text = "Foo 'Bar' Baz"
        self.assertEquals('Foo &apos;Bar&apos; Baz', escape_html(text))

    def test_escapes_ampersand(self):
        text = "Foo &Bar& Baz"
        self.assertEquals('Foo &amp;Bar&amp; Baz', escape_html(text))

    def test_escapes_empty_string_returns_empty_string(self):
        text = ''
        self.assertEquals('', escape_html(text))

    def test_escapes_none_returns_none(self):
        text = None
        self.assertEquals(None, escape_html(text))


class TestChecksum(TestCase):

    def test_md5_checksum(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'test.txt')
        alg, chksum = file_checksum(filename)
        self.assertEqual(alg, u'MD5')
        self.assertEqual(chksum, 'a51445bd8ffce9a6b90199f3fd72715a')

    def test_md5_checksum_with_multiple_chunks(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'test.txt')
        alg, chksum = file_checksum(filename, chunksize=100)
        self.assertEqual(alg, u'MD5')
        self.assertEqual(chksum, 'a51445bd8ffce9a6b90199f3fd72715a')

    def test_sha256_checksum(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'test.txt')
        alg, chksum = file_checksum(filename, algorithm=u'SHA256')
        self.assertEqual(alg, u'SHA256')
        self.assertEqual(chksum, '2cbe78150099d95789ceb5606818eeefccc7228cedd9bbe9cf7ce6af7071abd2')

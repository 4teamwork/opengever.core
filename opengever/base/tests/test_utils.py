from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from ftw.testing import MockTestCase
from mock import call
from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.base.utils import escape_html
from opengever.base.utils import file_checksum
from opengever.base.utils import get_date_with_delta_excluding_weekends
from opengever.base.utils import is_administrator
from opengever.base.utils import is_manager
from opengever.base.utils import is_transition_allowed
from opengever.base.utils import safe_int
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
        self.request = self.mock().proxy({}, count=False)

    def test_set_empty_filename(self):
        # HTTP_USER_AGENT
        self.request.get.return_value = ''

        set_attachment_content_disposition(self.request, '')

        self.request.response.setHeader.assert_not_called()

    def test_set_ms_filename(self):
        """ In Ms we must remove the quotes.
        """
        # HTTP_USER_AGENT
        self.request.get.return_value = 'MSIE'

        set_attachment_content_disposition(self.request, 'MS Name')

        self.request.response.setHeader.assert_called_with(
            'Content-disposition',
            'attachment; filename=%s' % quote('MS Name'))

    def test_filename(self):
        """ Normaly we have the filename in quotes
        """
        # HTTP_USER_AGENT
        self.request.get.return_value = 'DEF'

        set_attachment_content_disposition(self.request, 'Default Name')

        self.request.response.setHeader.assert_called_with(
            'Content-disposition',
            'attachment; filename="%s"' % 'Default Name')

    def test_with_file(self):
        # HTTP_USER_AGENT
        self.request.get.return_value = 'DEF'

        monk_file = NamedFile('bla bla', filename=u'test.txt')
        set_attachment_content_disposition(
            self.request, 'Default Name', file=monk_file)

        self.request.response.setHeader.assert_has_calls(
            [call('Content-Type', 'text/plain'),
             call('Content-Length', 7),
             call('Content-disposition', 'attachment; filename="%s"' % 'Default Name')])


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


class TestSafeInt(TestCase):

    def test_transparently_returns_int(self):
        value = 3
        self.assertEquals(3, safe_int(value))

    def test_casts_string_to_int(self):
        value = '3'
        self.assertEquals(3, safe_int(value))

    def test_defaults_to_zero(self):
        value = 'not an int'
        self.assertEqual(0, safe_int(value))

    def test_custom_default_value(self):
        value = 'not an int'
        self.assertEqual(7, safe_int(value, 7))


class TestIsAdministrator(IntegrationTestCase):

    def test_is_administrator_with_regular_user(self):
        self.assertFalse(is_administrator(user=self.regular_user))
        self.login(self.regular_user)
        self.assertFalse(is_administrator())

    def test_is_administrator_with_administrator(self):
        self.assertTrue(is_administrator(user=self.administrator))
        self.login(self.administrator)
        self.assertTrue(is_administrator())

    def test_is_administrator_with_limited_admin(self):
        self.assertTrue(is_administrator(user=self.limited_admin))
        self.login(self.limited_admin)
        self.assertTrue(is_administrator())


class TestIsManager(IntegrationTestCase):

    def test_is_manager_with_regular_user(self):
        self.assertFalse(is_manager(user=self.regular_user))
        self.login(self.regular_user)
        self.assertFalse(is_manager())

    def test_is_manager_with_administrator(self):
        self.assertFalse(is_manager(user=self.administrator))
        self.login(self.administrator)
        self.assertFalse(is_manager())

    def test_is_manager_with_limited_admin(self):
        self.assertFalse(is_manager(user=self.limited_admin))
        self.login(self.limited_admin)
        self.assertFalse(is_manager())

    def test_is_manager_with_manager(self):
        self.assertTrue(is_manager(user=self.manager))
        self.login(self.manager)
        self.assertTrue(is_manager())


class TestGetDateWithDeltaExcludingWeekends(TestCase):

    def test_get_date_with_delta_excluding_weekends_adds_the_day_offset(self):
        # Freeze on monday
        with freeze(datetime(2023, 3, 6, 0, 0)):
            delta = 4
            self.assertEqual(
                date(2023, 3, 10),  # Friday
                get_date_with_delta_excluding_weekends(datetime.today(), delta).date())

    def test_get_date_with_delta_excluding_weekends_adds_the_day_offset_and_ignores_weekends(self):
        # Freeze on monday
        with freeze(datetime(2023, 3, 6, 0, 0)):
            delta = 5
            self.assertEqual(
                date(2023, 3, 13),  # Next monday
                get_date_with_delta_excluding_weekends(datetime.today(), delta).date())

            delta = 20
            self.assertEqual(
                date(2023, 4, 3),  # Monday in one month
                get_date_with_delta_excluding_weekends(datetime.today(), delta).date())


class TestIsTransitionAllowed(IntegrationTestCase):

    def test_is_transition_allowed_checks_transition_guards(self):
        self.login(self.regular_user)

        self.assertTrue(is_transition_allowed(self.document, self.document.finalize_transition))

        self.checkout_document(self.document)

        self.assertFalse(is_transition_allowed(self.document, self.document.finalize_transition))

from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase


class TestFormatParticipant(FunctionalTestCase):

    def test_return_fullname_if_no_email(self):
        member = create(Builder('member').having(
            firstname=u'Hans', lastname=u'M\xfcller'))

        self.assertEqual(u'M\xfcller Hans', member.get_title())

    def test_return_fullname_with_email(self):
        member = create(Builder('member').having(
            firstname=u'Hans',
            lastname=u'M\xfcller',
            email=u'hans.mueller@example.com'))

        self.assertEqual(
            u'M\xfcller Hans (<a href="mailto:hans.mueller@example.com">hans.mueller@example.com</a>)',
            member.get_title())

    def test_return_fullname_without_linked_email(self):
        member = create(Builder('member').having(
            firstname=u'Hans',
            lastname=u'M\xfcller',
            email=u'hans.mueller@example.com'))

        self.assertEqual(
            u'M\xfcller Hans (hans.mueller@example.com)',
            member.get_title(show_email_as_link=False))

    def test_result_is_html_escaped(self):
        member = create(Builder('member').having(
            firstname=u'Hans',
            lastname=u'<script></script>M\xfcller'))

        self.assertEqual(
            u'&lt;script&gt;&lt;/script&gt;M\xfcller Hans',
            member.get_title())

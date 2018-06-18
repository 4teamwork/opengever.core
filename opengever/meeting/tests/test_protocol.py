from opengever.testing import IntegrationTestCase
from opengever.base.model import create_session


class TestMember(IntegrationTestCase):

    def test_return_fullname_if_no_email(self):
        self.login(self.meeting_user)
        self.committee_president.model.email = None

        self.assertEqual(
            u'Sch\xf6ller Heidrun',
            self.committee_president.model.get_title())

    def test_return_linked_email_by_default(self):
        self.login(self.meeting_user)

        self.assertEqual(
            u'Sch\xf6ller Heidrun (<a href="mailto:h.schoeller@web.de">h.schoeller@web.de</a>)',
            self.committee_president.model.get_title())

    def test_return_unlinked_title_if_desired(self):
        self.login(self.meeting_user)

        self.assertEqual(
            u'Sch\xf6ller Heidrun (h.schoeller@web.de)',
            self.committee_president.model.get_title(show_email_as_link=False))

    def test_result_is_html_escaped(self):
        self.login(self.meeting_user)
        self.committee_president.model.lastname = u'<script></script>Sch\xf6ller'
        self.committee_president.model.email = None

        create_session().flush()  # the fullname property needs a nudge
        self.assertEqual(
            u'&lt;script&gt;&lt;/script&gt;Sch\xf6ller Heidrun',
            self.committee_president.model.get_title())

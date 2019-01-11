from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.testing.pages import byline


class TestMeetingByline(IntegrationTestCase):
    features = ('meeting',)

    @browsing
    def test_items(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)
        self.assertEquals(
            [('State:', 'Pending'),
             ('Start:', 'Sep 12, 2016 05:30 PM'),
             ('End:', 'Sep 12, 2016 07:00 PM'),
             ('Presidency:', u'Sch\xf6ller Heidrun'),
             ('Secretary:', u'Secretary C\xf6mmittee'),
             ('Location:', u'B\xfcren an der Aare'),
             ('Meeting dossier:', 'Sitzungsdossier 9/2017')],
            byline.text_items())

    @browsing
    def test_dossier_link(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)
        byline.by_label()['Meeting dossier:'].css('a').first.click()
        self.assertEquals(self.meeting_dossier, browser.context)

    @browsing
    def test_dossier_linked_but_no_breadcrumbs_when_unauthorized(self, browser):
        self.login(self.meeting_user, browser)

        browser.open(self.meeting)
        item = byline.by_label()['Meeting dossier:']
        self.assertTrue(item.css('a').first)
        self.assertTrue(item.css('.rollover-breadcrumb').first)

        self.meeting_dossier.__ac_local_roles_block__ = True
        browser.open(self.meeting)
        item = byline.by_label()['Meeting dossier:']
        self.assertTrue(item.css('a').first)
        self.assertFalse(item.css('.rollover-breadcrumb'))

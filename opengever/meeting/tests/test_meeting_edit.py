from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import plone
from ftw.testbrowser.pages import statusmessages
from ftw.testing import freeze
from opengever.base.date_time import utcnow_tz_aware
from opengever.base.model import create_session
from opengever.testing import IntegrationTestCase
from opengever.testing.pages import byline


class TestEditMeeting(IntegrationTestCase):
    features = ('meeting', 'word-meeting')

    @browsing
    def test_edit_meeting_visibile_to_committe_responsible(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)
        self.assertIn('Edit', editbar.contentviews())

    @browsing
    def test_edit_meeting_not_visibile_to_meeting_(self, browser):
        self.login(self.meeting_user, browser)
        browser.open(self.meeting)

        self.assertEquals([], editbar.contentviews())

    @browsing
    def test_can_edit_meeting_secretary(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting, view='edit-meeting')

        self.assertIsNotNone(browser.css('#form-widgets-secretary'))

    @browsing
    def test_edit_meeting_metadata(self, browser):
        self.maxDiff = None
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)

        self.assertEquals(u'9. Sitzung der Rechnungspr\xfcfungskommission',
                          plone.first_heading())
        self.assertEquals(
            {'State:': 'Pending',
             'Start:': 'Sep 12, 2016 05:30 PM',
             'End:': 'Sep 12, 2016 07:00 PM',
             'Presidency:': u'Sch\xf6ller Heidrun',
             'Secretary:': u'M\xfcller Henning',
             'Location:': u'B\xfcren an der Aare',
             'Meeting dossier:': 'Sitzungsdossier 9/2017'},
            byline.text_dict())

        editbar.contentview('Edit').click()
        browser.fill({'Title': u'New Meeting Title',
                      'Other Participants': 'Staatsanwalt',
                      'Protocol start-page': '27',
                      'Location': 'Sitzungszimmer 3',
                      'Start': '13.10.2016 08:00',
                      'End': '13.10.2016 10:00'}).save()
        statusmessages.assert_message('Changes saved')

        self.assertEquals('New Meeting Title', plone.first_heading())
        self.assertEquals(
            {'State:': 'Pending',
             'Start:': 'Oct 13, 2016 08:00 AM',
             'End:': 'Oct 13, 2016 10:00 AM',
             'Presidency:': u'Sch\xf6ller Heidrun',
             'Secretary:': u'M\xfcller Henning',
             'Location:': u'Sitzungszimmer 3',
             'Meeting dossier:': 'New Meeting Title'},
            byline.text_dict())

        self.assertEquals('New Meeting Title', self.meeting_dossier.title)

    @browsing
    def test_edit_meeting_locks_the_content(self, browser1):
        self.login(self.committee_responsible)
        with browser1.clone() as browser2:
            browser1.login(self.committee_responsible)
            browser2.login(self.administrator)

            browser1.open(self.meeting, view='edit-meeting')
            self.assertEquals('edit-meeting', plone.view(browser1))

            browser2.open(self.meeting, view='edit-meeting')
            self.assertEquals('view', plone.view(browser2))
            statusmessages.assert_message(
                u'This item was locked by M\xfcller Fr\xe4nzi 1 minute ago.'
                u' If you are certain this user has abandoned the object,'
                u' you may the object. You will then be able to edit it.',
                browser=browser2)

            browser1.click_on('Cancel')
            browser2.open(self.meeting, view='edit-meeting')
            self.assertEquals('edit-meeting', plone.view(browser2))

    @browsing
    def test_edit_meeting_reports_write_conflicts(self, tab1):
        self.login(self.committee_responsible, tab1)
        with tab1.clone() as tab2:
            with freeze(utcnow_tz_aware()) as clock:
                tab1.open(self.meeting, view='edit-meeting')
                tab2.open(self.meeting, view='edit-meeting')

                tab1.fill({'Title': u'Title by tab 1'}).save()
                statusmessages.assert_message('Changes saved', browser=tab1)
                self.assertEquals(u'Title by tab 1', plone.first_heading(browser=tab1))
                create_session().flush()
                clock.forward(minutes=1)

                tab2.fill({'Title': u'Title by tab 2'}).save()
                statusmessages.assert_message(
                    'Your changes were not saved,'
                    ' the protocol has been modified in the meantime.', browser=tab2)
                tab2.open(self.meeting)
                self.assertEquals(u'Title by tab 1', plone.first_heading(browser=tab2))

    @browsing
    def test_cannot_edit_closed_meeting(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.decided_meeting)
        self.assertNotIn('Edit', editbar.contentviews())
        with browser.expect_unauthorized():
            browser.open(self.decided_meeting, view='edit-meeting')

    @browsing
    def test_action_is_only_visible_when_word_feature_enabled(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)
        self.assertIn('Edit', editbar.contentviews())

        self.deactivate_feature('word-meeting')
        browser.reload()
        self.assertNotIn('Edit', editbar.contentviews())

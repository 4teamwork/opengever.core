from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestUnscheduledProposals(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_list_unscheduled_proposals_json(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting, view='unscheduled_proposals')

        self.assertEquals(
            {u'items': [
                {u'submitted_proposal_url': u'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/submitted-proposal-1',
                 u'schedule_url': u'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/meeting-1/unscheduled_proposals/1/schedule',
                 u'title': u'Vertragsentwurf f\xfcr weitere Bearbeitung bewilligen'},
                {u'submitted_proposal_url': u'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/submitted-proposal-4',
                 u'schedule_url': u'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/meeting-1/unscheduled_proposals/4/schedule',
                 u'title': u'\xc4nderungen am Personalreglement'}
            ]},
            browser.json
        )

    @browsing
    def test_schedule_proposal(self, browser):
        self.login(self.committee_responsible, browser)

        view = 'unscheduled_proposals/{}/schedule'.format(
                self.submitted_proposal.load_model().id
        )

        browser.open(self.meeting, view=view)
        self.assertEqual([{u'messageTitle': u'Information',
                           u'message': u'Scheduled Successfully',
                           u'messageClass': u'info'}],
                         browser.json.get('messages'))

        self.assertEqual(1, len(self.meeting.model.agenda_items))
        self.assertEqual(
            self.submitted_proposal.load_model(),
            self.meeting.model.agenda_items[0].proposal
        )

    @browsing
    def test_raise_forbidden_when_meeting_is_not_editable(self, browser):
        self.login(self.committee_responsible, browser)

        view = 'unscheduled_proposals/{}/schedule'.format(
                self.submitted_proposal.load_model().id
        )

        with browser.expect_http_error(code=403):
            browser.open(self.decided_meeting, view=view)

    @browsing
    def test_raise_notfound_with_invalid_proposal_id(self, browser):
        self.login(self.committee_responsible, browser)

        with browser.expect_http_error(reason='Not Found'):
            browser.open(self.meeting,
                         view='unscheduled_proposals/1337/schedule')

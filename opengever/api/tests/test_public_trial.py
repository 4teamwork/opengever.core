from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
import json


class TestPublicTrialStatusPatch(IntegrationTestCase):

    @browsing
    def test_raises_unauthorized_if_public_trial_edit_form_is_not_accessible(self, browser):
        self.login(self.regular_user, browser)

        self.set_workflow_state('dossier-state-inactive', self.dossier)
        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open(
                '{}/@public-trial-status'.format(self.document.absolute_url()),
                method='PATCH', headers=self.api_headers)

    @browsing
    def test_updates_public_trial_data_successfully(self, browser):
        self.login(self.regular_user, browser)

        data = {
            'public_trial': 'limited-public',
            'public_trial_statement': u'Keine heiklen Daten.'}

        browser.open(
            '{}/@public-trial-status'.format(self.document.absolute_url()),
            method='PATCH', data=json.dumps(data), headers=self.api_headers)

        self.assertEquals(204, browser.status_code)
        self.assertEquals('limited-public', self.document.public_trial)
        self.assertEquals(u'Keine heiklen Daten.',
                          self.document.public_trial_statement)

    @browsing
    def test_raises_forbidden_when_trying_to_update_other_fields(self, browser):
        self.login(self.regular_user, browser)

        data = {
            'public_trial': 'limited-public',
            'title': u'Test'}

        with browser.expect_http_error(code=403, reason='Forbidden'):
            browser.open(
                '{}/@public-trial-status'.format(self.document.absolute_url()),
                method='PATCH', data=json.dumps(data), headers=self.api_headers)

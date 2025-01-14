from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestWorkflowBulkTransition(IntegrationTestCase):

    @browsing
    def test_get_information_about_an_object(self, browser):
        self.login(self.regular_user, browser=browser)

        url = "{}/@workflow-bulk-transition".format(self.dossier.absolute_url())

        browser.open(url, headers=self.api_headers)

        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            {
                u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/@workflow-bulk-transition',
                u'transitions': [
                    {
                        u'source_state_id': u'dossier-state-active',
                        u'target_state_id': u'dossier-state-resolved',
                        u'transition_id': u'dossier-transition-resolve',
                        u'workflow_id': u'opengever_dossier_workflow'
                    },
                    {
                        u'source_state_id': u'dossier-state-resolved',
                        u'target_state_id': u'dossier-state-active',
                        u'transition_id': u'dossier-transition-reactivate',
                        u'workflow_id': u'opengever_dossier_workflow'
                    }]
            }, browser.json)

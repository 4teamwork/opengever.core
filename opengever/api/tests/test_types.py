from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase

GEVER_TYPES = ['ftw.mail.mail',
               'opengever.contact.contact',
               'opengever.contact.contactfolder',
               'opengever.disposition.disposition',
               'opengever.document.document',
               'opengever.dossier.businesscasedossier',
               'opengever.dossier.dossiertemplate',
               'opengever.dossier.templatefolder',
               'opengever.inbox.container',
               'opengever.inbox.forwarding',
               'opengever.inbox.inbox',
               'opengever.inbox.yearfolder',
               'opengever.meeting.committee',
               'opengever.meeting.committeecontainer',
               'opengever.meeting.meetingdossier',
               'opengever.meeting.meetingtemplate',
               'opengever.meeting.paragraphtemplate',
               'opengever.meeting.proposal',
               'opengever.meeting.proposaltemplate',
               'opengever.meeting.sablontemplate',
               'opengever.meeting.submittedproposal',
               'opengever.private.dossier',
               'opengever.private.folder',
               'opengever.private.root',
               'opengever.repository.repositoryfolder',
               'opengever.repository.repositoryroot',
               'opengever.task.task',
               'opengever.tasktemplates.tasktemplate',
               'opengever.tasktemplates.tasktemplatefolder',
               'opengever.workspace.folder',
               'opengever.workspace.root',
               'opengever.workspace.workspace',
               'Plone%20Site']


class TestPloneRestAPI(IntegrationTestCase):

    @browsing
    def test_rest_api(self, browser):
        self.login(self.regular_user, browser)
        for content_type in GEVER_TYPES:
            browser.open(self.portal.absolute_url() + '/@types/{}'.format(content_type),
                         method='GET', headers={'Accept': 'application/json'})
            self.assertEqual(200, browser.status_code)

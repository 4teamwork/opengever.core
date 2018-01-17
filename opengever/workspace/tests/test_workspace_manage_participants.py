from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


def get_entry_by_userid(entries, userid):
    for entry in entries:
        if entry['userid'] == userid:
            return entry
    return None


class TestWorkspaceManageParticipants(IntegrationTestCase):

    def setUp(self):
        super(TestWorkspaceManageParticipants, self).setUp()
        # self.storage = InvitationStorage(self.workspace)

    @browsing
    def test_list_all_current_participants(self, browser):
        self.login(self.workspace_admin, browser=browser)
        browser.visit(self.workspace, view='manage-participants')

        self.assertItemsEqual(
            [
                {u'can_manage': True,
                 u'name': u'Schr\xf6dinger B\xe9atrice (beatrice.schrodinger@gever.local)',
                 u'roles': [u'WorkspaceMember'],
                 u'type_': u'user',
                 u'userid': u'beatrice.schrodinger'},
                {u'can_manage': False,
                 u'name': u'Hugentobler Fridolin (fridolin.hugentobler@gever.local)',
                 u'roles': [u'WorkspaceAdmin'],
                 u'type_': u'user',
                 u'userid': u'fridolin.hugentobler'},
                {u'can_manage': True,
                 u'name': u'Fr\xf6hlich G\xfcnther (gunther.frohlich@gever.local)',
                 u'roles': [u'WorkspaceOwner'],
                 u'type_': u'user',
                 u'userid': u'gunther.frohlich'},
                {u'can_manage': True,
                 u'name': u'Peter Hans (hans.peter@gever.local)',
                 u'roles': [u'WorkspaceGuest'],
                 u'type_': u'user',
                 u'userid': u'hans.peter'},
            ],
            browser.json
        )

    @browsing
    def test_current_logged_in_admin_cannot_manage_himself(self, browser):
        self.login(self.workspace_admin, browser=browser)
        browser.visit(self.workspace, view='manage-participants')

        self.assertFalse(
            get_entry_by_userid(browser.json, 'fridolin.hugentobler')['can_manage'],
            'The admin should not be able to manage himself')
        self.assertTrue(
            get_entry_by_userid(browser.json, 'hans.peter')['can_manage'],
            'The admin should be able to manage hans.peter')

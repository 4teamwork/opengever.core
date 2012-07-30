from ftw.testing import MockTestCase
from opengever.ogds.base.interfaces import IContactInformation
from opengever.tabbedview.browser.personal_overview import PersonalOverview


class TestPersonalOverview(MockTestCase):

    def test_user_is_allowed_to_view(self):
        context = self.stub()
        request = self.stub()

        info = self.stub()
        self.mock_utility(info, IContactInformation, name=u"")

        membership = self.stub()
        member = self.stub()
        self.mock_tool(membership, 'portal_membership')
        self.expect(membership.getAuthenticatedMember()).result(member)

        with self.mocker.order():
            self.expect(info.is_client_assigned()).result(True)

            self.expect(info.is_client_assigned()).result(False)
            self.expect(member.has_role('Administrator')).result(True)

            self.expect(info.is_client_assigned()).result(False)
            self.expect(member.has_role('Administrator')).result(False)
            self.expect(member.has_role('Manager')).result(True)

            self.expect(info.is_client_assigned()).result(False)
            self.expect(member.has_role('Administrator')).result(False)
            self.expect(member.has_role('Manager')).result(False)

        self.replay()

        view = PersonalOverview(context, request)

        self.assertTrue(view.user_is_allowed_to_view())
        self.assertTrue(view.user_is_allowed_to_view())
        self.assertTrue(view.user_is_allowed_to_view())
        self.assertFalse(view.user_is_allowed_to_view())


    def test_get_tabs(self):
        context = self.stub()
        request = self.stub()

        info = self.stub()
        self.mock_utility(info, IContactInformation, name=u"")

        membership = self.stub()
        member = self.stub()
        self.mock_tool(membership, 'portal_membership')
        self.expect(membership.getAuthenticatedMember()).result(member)

        with self.mocker.order():
            self.expect(info.is_user_in_inbox_group()).result(True)

            self.expect(info.is_user_in_inbox_group()).result(False)
            self.expect(member.has_role('Administrator')).result(True)

            self.expect(info.is_user_in_inbox_group()).result(False)
            self.expect(member.has_role('Administrator')).result(False)
            self.expect(member.has_role('Manager')).result(False)

        self.replay()

        view = PersonalOverview(context, request)

        tabs = view.get_tabs()
        self.assertEquals(
            ['mydossiers', 'mydocuments', 'mytasks', 'myissuedtasks',
             'alltasks', 'allissuedtasks'],
            [tab.get('id') for tab in tabs])

        tabs = view.get_tabs()
        self.assertEquals(
            ['mydossiers', 'mydocuments', 'mytasks', 'myissuedtasks',
             'alltasks', 'allissuedtasks'],
            [tab.get('id') for tab in tabs])

        tabs = view.get_tabs()
        self.assertEquals(
            ['mydossiers', 'mydocuments', 'mytasks', 'myissuedtasks'],
            [tab.get('id') for tab in tabs])

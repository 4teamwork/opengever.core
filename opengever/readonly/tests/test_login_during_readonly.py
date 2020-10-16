from DateTime import DateTime
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from opengever.testing.readonly import ZODBStorageInReadonlyMode
from plone import api
from plone.app.testing import TEST_USER_ID
import transaction


class TestLoginDuringReadOnlyMode(FunctionalTestCase):

    @browsing
    def test_set_login_times_doesnt_prevent_login_during_readonly(self, browser):
        membership_tool = api.portal.get_tool('portal_membership')

        with ZODBStorageInReadonlyMode():
            browser.login()
            membership_tool.setLoginTimes()
            transaction.commit()

        member = membership_tool.getAuthenticatedMember()
        self.assertEqual(TEST_USER_ID, member.getId())
        self.assertEqual(DateTime('2000/01/01'), member.getProperty('last_login_time'))

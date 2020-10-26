from ftw.testbrowser import browsing
from opengever.ogds.models.user import User
from opengever.testing import IntegrationTestCase
from opengever.testing.readonly import ZODBStorageInReadonlyMode


class TestLastLoginReadOnlySQL(IntegrationTestCase):

    @browsing
    def test_doesnt_write_last_login_to_sql_in_ro_mode(self, browser):
        userid = self.regular_user.getId()
        ogds_user = User.get(userid)
        self.assertIsNone(ogds_user.last_login)

        with ZODBStorageInReadonlyMode():
            browser.visit(view='login_form')
            browser.fill({'Login Name': userid, 'Password': 'secret'}).submit()
            ogds_user = User.query.get_by_userid(userid)

        self.assertIsNone(ogds_user.last_login)

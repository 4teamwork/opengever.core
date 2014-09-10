from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.browser.resolveoguid import ResolveOGUIDView
from opengever.testing import FunctionalTestCase
from plone.app.testing import logout
from zExceptions import Unauthorized
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class TestResolveOGUIDView(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestResolveOGUIDView, self).setUp()

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_user().with_org_unit().with_admin_unit(
                public_url=self.portal.absolute_url(),
                unit_id='client1'
                ))
        self.task = create(Builder('task'))
        self.task_id = getUtility(IIntIds).getId(self.task)

    @browsing
    def test_check_permissions_fails_with_nobody(self, browser):
        logout()
        url = ResolveOGUIDView.url_for('client1:{}'.format(self.task_id),
                                       self.admin_unit)
        with self.assertRaises(Unauthorized):
            browser.open(url)

    @browsing
    def test_redirect_if_correct_client(self, browser):
        url = ResolveOGUIDView.url_for('client1:{}'.format(self.task_id),
                                       self.admin_unit)
        browser.login().open(url)
        self.assertEqual(self.task.absolute_url(), browser.url)

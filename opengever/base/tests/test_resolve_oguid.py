from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.core import LIB_REQUESTS
from opengever.base.browser.resolveoguid import ResolveOGUIDView
from opengever.testing import FunctionalTestCase
from plone.app.testing import logout
from zExceptions import Unauthorized
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class TestResolveOGUIDView(FunctionalTestCase):

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

    #XXX can't test this now. damnit.
    # @browsing
    # def test_redirect_to_other_client(self, browser):
    #     foo_unit = create(Builder('admin_unit').id('foo')
    #                       .having(public_url='http://example.com'))
    #     url = ResolveOGUIDView.url_for('foo:123')
    #     try:
    #         browser.open(url, library=LIB_REQUESTS)
    #     except Exception as e:
    #         import pudb; pudb.set_trace()
    #     import pudb; pudb.set_trace()

#     def test_redirect_to_other_client(self):
#         oguid = 'client2:5'
#         client2_url = 'http://otherhost/client2'
#         target_url = '%s/@@resolve_oguid?oguid=%s' % (client2_url, oguid)

#         info = self.mocker.mock()
#         self.mock_utility(info, IContactInformation)
#         self.expect(info.get_client_by_id('client2').public_url).result(
#             client2_url)

#         request = self.mocker.mock()
#         self.expect(request.get('oguid')).result('client2:5')
#         self.expect(request.RESPONSE.redirect(target_url)).result('REDIRECT')

#         self.replay()

#         view = ResolveOGUIDView(object(), request)
#         self.assertEqual(view.render(), 'REDIRECT')

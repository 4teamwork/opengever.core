from AccessControl.SecurityManagement import SpecialUsers
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from mocker import Mocker, Expect
from opengever.base.browser.resolveoguid import ResolveOGUIDView
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.interfaces import IContactInformation
from plone.mocktestcase import MockTestCase
from plone.registry.interfaces import IRegistry
from unittest2 import TestCase
from zExceptions import Unauthorized
from zope.app.component.hooks import setSite
from zope.component import getGlobalSiteManager
from zope.interface import alsoProvides
from zope.intid.interfaces import IIntIds


class TestResolveOGUIDView(MockTestCase, TestCase):

    def setUp(self):
        self.testcase_mocker = Mocker()
        expect = Expect(self.testcase_mocker)

        sm = getGlobalSiteManager()
        siteroot = self.create_dummy(
            id='siteroot',
            getSiteManager=lambda: sm)
        alsoProvides(siteroot, IPloneSiteRoot)
        setSite(siteroot)

        registry = self.testcase_mocker.mock()
        self.mock_utility(registry, IRegistry)

        proxy = self.create_dummy(client_id='client1')
        expect(registry.forInterface(IClientConfiguration)).result(
            proxy).count(0, None)

        self.testcase_mocker.replay()

    def tearDown(self):
        setSite(None)

        self.testcase_mocker.restore()
        self.testcase_mocker.verify()

    def test_check_permissions_fails_with_nobody(self):
        mtool = self.mocker.mock()
        self.expect(mtool.getAuthenticatedMember()).result(
            SpecialUsers.nobody)
        self.mock_tool(mtool, 'portal_membership')

        self.replay()

        view = ResolveOGUIDView(object(), object())

        with TestCase.assertRaises(self, Unauthorized):
            view._check_permissions(object())


    def test_check_permission_fails_without_view_permission(self):
        obj = self.mocker.mock()

        mtool = self.mocker.mock()
        self.expect(mtool.getAuthenticatedMember().checkPermission(
                'View', obj)).result(False)
        self.mock_tool(mtool, 'portal_membership')

        self.replay()

        view = ResolveOGUIDView(object(), object())

        with TestCase.assertRaises(self, Unauthorized):
            view._check_permissions(obj)

    def test_redirect_to_other_client(self):
        oguid = 'client2:5'
        client2_url = 'http://otherhost/client2'
        target_url = '%s/@@resolve_oguid?oguid=%s' % (client2_url, oguid)

        info = self.mocker.mock()
        self.mock_utility(info, IContactInformation)
        self.expect(info.get_client_by_id('client2').public_url).result(
            client2_url)

        request = self.mocker.mock()
        self.expect(request.get('oguid')).result('client2:5')
        self.expect(request.RESPONSE.redirect(target_url)).result('REDIRECT')

        self.replay()

        view = ResolveOGUIDView(object(), request)
        self.assertEqual(view.render(), 'REDIRECT')

    def test_redirect_if_correct_client(self):
        absolute_url = 'http://anyhost/client1/somedossier'
        obj = self.mocker.mock()
        self.expect(obj.absolute_url()).result(absolute_url)

        context = object()

        request = self.mocker.mock()
        self.expect(request.get('oguid')).result('client1:444')
        self.expect(request.RESPONSE.redirect(absolute_url)).result(
            'redirected')

        intids = self.mocker.mock()
        self.expect(intids.getObject(444)).result(obj)
        self.mock_utility(intids, IIntIds)

        mtool = self.mocker.mock()
        self.expect(mtool.getAuthenticatedMember().checkPermission(
                'View', obj)).result(True)
        self.mock_tool(mtool, 'portal_membership')

        self.replay()

        view = ResolveOGUIDView(context, request)
        self.assertEqual(view.render(), 'redirected')

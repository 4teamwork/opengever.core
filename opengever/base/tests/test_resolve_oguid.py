from AccessControl.SecurityManagement import SpecialUsers
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from mocker import Mocker, Expect
from opengever.base.browser.resolveoguid import ResolveOGUIDView
from opengever.ogds.base.interfaces import IClientConfiguration
from plone.mocktestcase import MockTestCase
from plone.registry.interfaces import IRegistry
from unittest2 import TestCase
from zExceptions import NotFound
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

        with TestCase.assertRaises(self, NotFound):
            view._check_permissions(object())


    def test_check_permission_fails_without_view_permission(self):
        obj = self.mocker.mock()

        mtool = self.mocker.mock()
        self.expect(mtool.getAuthenticatedMember().checkPermission(
                'View', obj)).result(False)
        self.mock_tool(mtool, 'portal_membership')

        self.replay()

        view = ResolveOGUIDView(object(), object())

        with TestCase.assertRaises(self, NotFound):
            view._check_permissions(obj)

    def test_fails_if_wrong_client(self):
        request = self.mocker.mock()
        self.expect(request.get('oguid')).result('wrongclient:5')

        self.replay()

        view = ResolveOGUIDView(object(), request)

        with TestCase.assertRaises(self, AssertionError):
            view.render()

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

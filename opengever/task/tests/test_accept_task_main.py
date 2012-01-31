from Products.CMFPlone.interfaces import IPloneSiteRoot
from ftw.testing import MockTestCase
from grokcore.component.testing import grok
from mocker import Mocker, expect
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.interfaces import IContactInformation
from opengever.task.browser.accept import main
from opengever.task.task import ITask
from plone.registry.interfaces import IRegistry
from plone.testing import Layer
from plone.testing import zca
from zope.app.component.hooks import setSite
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.component import provideUtility
from zope.configuration import xmlconfig
from zope.interface import implements
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class AcceptTaskLayer(Layer):

    defaultBases = (zca.ZCML_DIRECTIVES,)

    def testSetUp(self):
        self.mocker = Mocker()
        self['configurationContext'] = zca.stackConfigurationContext(
            self.get('configurationContext'))

        self._load_zcml()
        self._mock_site_root()
        self._mock_utilities()

    def _load_zcml(self):
        import zope.annotation
        xmlconfig.file('configure.zcml', zope.annotation,
                       context=self['configurationContext'])

        import five.grok
        xmlconfig.file('meta.zcml', five.grok,
                       self['configurationContext'])

        import Products.Five
        xmlconfig.file('meta.zcml', Products.Five,
                       self['configurationContext'])

        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '<permission id="cmf.AddPortalContent" title="" />'
            '</configure>',
            self['configurationContext'])

        grok('opengever.task.browser.accept.main')

    def _mock_site_root(self):
        class SiteRoot(object):
            implements(IPloneSiteRoot)
            id = 'root'
            getSiteManager = getSiteManager

        self.root = SiteRoot()
        setSite(self.root)

    def _mock_utilities(self):
        self.registry = self.mocker.mock(count=False)
        provideUtility(self.registry, IRegistry)

        # mock "current client" configuration
        expect(self.registry.forInterface(
                IClientConfiguration).client_id).result('client1')

        # mock contact info utility
        self.info = self.mocker.mock(count=False)
        provideUtility(self.info, IContactInformation)

    def testTearDown(self):
        self.mocker.restore()
        self.mocker.verify()
        del self['configurationContext']


ACCEPT_TASK_LAYER = AcceptTaskLayer()


class TestAcceptTaskView(MockTestCase):

    layer = ACCEPT_TASK_LAYER

    def replay(self):
        self.layer.mocker.replay()
        super(TestAcceptTaskView, self).replay()

    def test_view_is_registered(self):
        task = self.providing_stub([ITask])
        request = self.providing_stub([IDefaultBrowserLayer])

        self.replay()

        view = getMultiAdapter((task, request), name='accept_task')

        self.assertTrue(isinstance(view, main.AcceptTask))

    def test_wizard_is_inactive_when_in_single_site_setup(self):
        expect(self.layer.info.get_clients()).result([object()])
        task = self.providing_stub([ITask])
        request = self.providing_stub([IDefaultBrowserLayer])

        self.replay()

        view = getMultiAdapter((task, request), name='accept_task')

        self.assertFalse(view.is_wizard_active())

    def test_wizard_is_active_in_multi_client_setup(self):
        expect(self.layer.info.get_clients()).result(
            [object(), object()])
        task = self.providing_stub([ITask])
        request = self.providing_stub([IDefaultBrowserLayer])

        self.replay()

        view = getMultiAdapter((task, request), name='accept_task')

        self.assertTrue(view.is_wizard_active())

    def test_successing_impossible_on_single_client_setup(self):
        expect(self.layer.info.get_clients()).result([object()])
        task = self.providing_stub([ITask])
        request = self.providing_stub([IDefaultBrowserLayer])

        self.replay()

        view = getMultiAdapter((task, request), name='accept_task')

        self.assertFalse(view.is_successing_possible())

    def test_client_internal_successing_impossible(self):
        expect(self.layer.info.get_clients()).result(
            [object(), object()])
        task = self.providing_stub([ITask])
        self.expect(task.responsible_client).result('client1')
        request = self.providing_stub([IDefaultBrowserLayer])

        self.replay()

        view = getMultiAdapter((task, request), name='accept_task')

        self.assertFalse(view.is_successing_possible())

    def test_client_external_successing_possible(self):
        expect(self.layer.info.get_clients()).result(
            [object(), object()])
        task = self.providing_stub([ITask])
        self.expect(task.responsible_client).result('client2')
        request = self.providing_stub([IDefaultBrowserLayer])

        self.replay()

        view = getMultiAdapter((task, request), name='accept_task')

        self.assertTrue(view.is_successing_possible())

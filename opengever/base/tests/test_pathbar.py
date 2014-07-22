from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.testing import create_client
from opengever.testing import FunctionalTestCase
from opengever.testing import set_current_client_id
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TestPathBar(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestPathBar, self).setUp()

        create_client()
        set_current_client_id(self.portal)

        root = create(Builder('repository_root').titled(u'Repository'))
        repo = create(Builder('repository')
                      .within(root)
                      .titled(u'Testposition'))
        self.dossier = create(Builder('dossier')
                         .within(repo)
                         .titled(u'Dossier 1'))

    def test_last_part_is_linked(self):
        self.browser.open(self.dossier.absolute_url())

        breadcrumb_links = self.browser.css('#portal-breadcrumbs a')
        self.assertEquals(
            ['Client1', 'Repository', '1. Testposition', 'Dossier 1'],
            [aa.plain_text() for aa in breadcrumb_links])

    def test_first_part_is_client_title(self):
        self.browser.open(self.dossier.absolute_url())

        breadcrumb_links = self.browser.css('#portal-breadcrumbs a')
        self.assertEquals(
            ['Client1', 'Repository', '1. Testposition', 'Dossier 1'],
            [aa.plain_text() for aa in breadcrumb_links])


class TestPathBarFallback(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestPathBarFallback, self).setUp()

        root = create(Builder('repository_root').titled(u'Repository'))
        repo = create(Builder('repository')
                      .within(root)
                      .titled(u'Testposition'))
        self.dossier = create(Builder('dossier')
                         .within(repo)
                         .titled(u'Dossier 1'))

    def test_fallback_when_client_is_not_found_is_home_label(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IClientConfiguration)
        proxy.client_id = u'not-existing'

        self.browser.open(self.dossier.absolute_url())

        breadcrumb_links = self.browser.css('#portal-breadcrumbs a')
        self.assertEquals(
            ['Home', 'Repository', '1. Testposition', 'Dossier 1'],
            [aa.plain_text() for aa in breadcrumb_links])

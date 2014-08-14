from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestPathBar(FunctionalTestCase):

    def setUp(self):
        super(TestPathBar, self).setUp()

        root = create(Builder('repository_root').titled(u'Repository'))
        repo = create(Builder('repository')
                      .within(root)
                      .titled(u'Testposition'))
        self.dossier = create(Builder('dossier')
                              .within(repo)
                              .titled(u'Dossier 1'))

    @browsing
    def test_first_part_is_org_unit_title(self, browser):
        browser.login().open(self.dossier)

        breadcrumb_links = browser.css('#portal-breadcrumbs a')
        self.assertEquals(
            ['Client1', 'Repository', '1. Testposition', 'Dossier 1'],
            breadcrumb_links.text)

    @browsing
    def test_last_part_is_linked(self, browser):
        browser.login().open(self.dossier)

        last_link = browser.css('#portal-breadcrumbs a')[-1]
        self.assertEqual(self.dossier.absolute_url(),
                         last_link.node.attrib['href'])


class TestPathBarFallback(FunctionalTestCase):
    use_default_fixture = False

    def setUp(self):
        super(TestPathBarFallback, self).setUp()

        create(Builder('fixture').with_org_unit().with_admin_unit())
        root = create(Builder('repository_root').titled(u'Repository'))
        repo = create(Builder('repository')
                      .within(root)
                      .titled(u'Testposition'))
        self.dossier = create(Builder('dossier')
                              .within(repo)
                              .titled(u'Dossier 1'))

    @browsing
    def test_fallback_when_client_is_not_found_is_home_label(self, browser):
        browser.login().open(self.dossier)

        breadcrumb_links = browser.css('#portal-breadcrumbs a')
        self.assertEquals(
            ['Home', 'Repository', '1. Testposition', 'Dossier 1'],
            breadcrumb_links.text)

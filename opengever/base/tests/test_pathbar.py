from opengever.testing import FunctionalTestCase
from ftw.builder import Builder
from ftw.builder import create


class TestPathBar(FunctionalTestCase):

    use_browser = True

    def test_last_part_is_linked(self):
        root = create(Builder('repository_root').titled(u'Repository'))
        repo = create(Builder('repository')
                      .within(root)
                      .titled(u'Testposition'))
        dossier = create(Builder('dossier')
                         .within(repo)
                         .titled(u'Dossier 1'))

        self.browser.open(dossier.absolute_url())

        breadcrumb_links = self.browser.css('#portal-breadcrumbs a')
        self.assertEquals(
            ['Home', 'Repository', '1. Testposition', 'Dossier 1'],
            [aa.plain_text() for aa in breadcrumb_links])

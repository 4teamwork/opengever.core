from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone.uuid.interfaces import IUUID


class TestNavigation(FunctionalTestCase):

    @browsing
    def test_dossier_navigation_json_is_valid(self, browser):
        root = create(Builder('repository_root'))
        folder = create(Builder('repository').within(root))
        root_dossier = create(Builder('dossier')
                              .titled(u'Root')
                              .having(description=u'The root dossier')
                              .within(folder))
        subdossier = create(Builder('dossier')
                            .titled(u'Subdossier')
                            .having(description=u'The sub-dossier')
                            .within(root_dossier))

        browser.login().visit(root_dossier, view='dossier_navigation.json')
        self.assert_json_equal(
            [{"text": "Root",
              "description": "The root dossier",
              "uid": IUUID(root_dossier),
              "url": root_dossier.absolute_url(),
              "nodes": [{"text": "Subdossier",
                         "description": "The sub-dossier",
                         "nodes": [],
                         "uid": IUUID(subdossier),
                         "url": subdossier.absolute_url(),
                         }],
              }],
            browser.json)

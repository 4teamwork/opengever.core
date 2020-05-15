from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone.uuid.interfaces import IUUID


class TestNavigation(FunctionalTestCase):

    def setUp(self):
        super(TestNavigation, self).setUp()
        self.root = create(Builder('repository_root'))
        self.folder = create(Builder('repository').within(self.root))
        self.main_dossier = create(Builder('dossier')
                                   .titled(u'Main')
                                   .having(description=u'The main dossier')
                                   .within(self.folder))

    @browsing
    def test_dossier_navigation_json_is_valid(self, browser):
        subdossier = create(Builder('dossier')
                            .titled(u'Subdossier')
                            .having(description=u'The sub-dossier')
                            .within(self.main_dossier))

        browser.login().visit(self.main_dossier,
                              view='dossier_navigation.json')
        self.assert_json_equal(
            [{"text": "Main",
              "description": "The main dossier",
              "uid": IUUID(self.main_dossier),
              "url": self.main_dossier.absolute_url(),
              "nodes": [{"text": "Subdossier",
                         "description": "The sub-dossier",
                         "nodes": [],
                         "uid": IUUID(subdossier),
                         "url": subdossier.absolute_url(),
                         }],
              }],
            browser.json)

    @browsing
    def test_empty_dossier_navigation(self, browser):
        browser.login().visit(self.main_dossier, view='dossier_navigation.json')
        self.assertEqual([], browser.json)

    @browsing
    def test_dossiers_are_sorted_by_title(self, browser):
        sub1 = create(Builder('dossier')
                      .titled(u'XXX')
                      .having(description=u'The XXX sub-dossier')
                      .within(self.main_dossier))

        sub2 = create(Builder('dossier')
                      .titled(u'AAA')
                      .having(description=u'The AAA sub-dossier')
                      .within(self.main_dossier))

        browser.login().visit(self.main_dossier,
                              view='dossier_navigation.json')
        self.assert_json_equal(
            [{"text": "Main",
              "description": "The main dossier",
              "uid": IUUID(self.main_dossier),
              "url": self.main_dossier.absolute_url(),
              "nodes": [{"text": "AAA",
                         "description": "The AAA sub-dossier",
                         "nodes": [],
                         "uid": IUUID(sub2),
                         "url": sub2.absolute_url(),
                         },
                        {"text": "XXX",
                         "description": "The XXX sub-dossier",
                         "nodes": [],
                         "uid": IUUID(sub1),
                         "url": sub1.absolute_url(),
                         }],
              }],
            browser.json)

    @browsing
    def test_only_show_active_subdossiers(self, browser):
        sub1 = create(Builder('dossier')
                      .titled(u'active')
                      .having(description=u'The active sub-dossier')
                      .within(self.main_dossier))

        create(Builder('dossier')
               .titled(u'archived')
               .having(description=u'The archived sub-dossier')
               .in_state('dossier-state-archived')
               .within(self.main_dossier))

        create(Builder('dossier')
               .titled(u'inactive(storniert)')
               .having(description=u'The inactive sub-dossier')
               .in_state('dossier-state-inactive')
               .within(self.main_dossier))

        create(Builder('dossier')
               .titled(u'resolved(abgeschlossen)')
               .having(description=u'The resolved sub-dossier')
               .in_state('dossier-state-resolved')
               .within(self.main_dossier))

        browser.login().visit(self.main_dossier,
                              view='dossier_navigation.json')
        self.assert_json_equal(
            [{"text": "Main",
              "description": "The main dossier",
              "uid": IUUID(self.main_dossier),
              "url": self.main_dossier.absolute_url(),
              "nodes": [
                        {"text": "active",
                         "description": "The active sub-dossier",
                         "nodes": [],
                         "uid": IUUID(sub1),
                         "url": sub1.absolute_url(),
                         }]
              }],
            browser.json)

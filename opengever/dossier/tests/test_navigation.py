from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import SolrIntegrationTestCase
from plone.uuid.interfaces import IUUID


class TestNavigation(SolrIntegrationTestCase):

    @browsing
    def test_dossier_navigation_json_is_valid(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(self.subdossier, view='dossier_navigation.json')

        self.assertEqual(
            [{"text": self.subdossier.Title(),
              "description": self.subdossier.Description(),
              "uid": IUUID(self.subdossier),
              "url": self.subdossier.absolute_url(),
              "nodes": [{"text": self.subsubdossier.Title(),
                         "description": self.subsubdossier.Description(),
                         "nodes": [],
                         "uid": IUUID(self.subsubdossier),
                         "url": self.subsubdossier.absolute_url(),
                         }],
              }],
            browser.json)

    @browsing
    def test_empty_dossier_navigation(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(self.empty_dossier, view='dossier_navigation.json')
        self.assertEqual([], browser.json)

    @browsing
    def test_dossiers_are_sorted_by_title(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(self.dossier, view='dossier_navigation.json')

        nodes = browser.json[0]['nodes']
        self.assertEqual(
            [n['text'] for n in nodes], sorted([n['text'] for n in nodes]))

    @browsing
    def test_only_show_active_subdossiers(self, browser):
        self.login(self.regular_user, browser=browser)

        sub1 = create(Builder('dossier')
                      .titled(u'active')
                      .having(description=u'The active sub-dossier')
                      .within(self.empty_dossier))

        create(Builder('dossier')
               .titled(u'archived')
               .having(description=u'The archived sub-dossier')
               .in_state('dossier-state-archived')
               .within(self.empty_dossier))

        create(Builder('dossier')
               .titled(u'inactive(storniert)')
               .having(description=u'The inactive sub-dossier')
               .in_state('dossier-state-inactive')
               .within(self.empty_dossier))

        create(Builder('dossier')
               .titled(u'resolved(abgeschlossen)')
               .having(description=u'The resolved sub-dossier')
               .in_state('dossier-state-resolved')
               .within(self.empty_dossier))

        self.commit_solr()
        browser.visit(self.empty_dossier, view='dossier_navigation.json')

        self.assertEqual(
            [{
                "text": self.empty_dossier.Title(),
                "description": self.empty_dossier.Description(),
                "uid": IUUID(self.empty_dossier),
                "url": self.empty_dossier.absolute_url(),
                "nodes": [{
                    "text": "active",
                    "description": "The active sub-dossier",
                    "nodes": [],
                    "uid": IUUID(sub1),
                    "url": sub1.absolute_url(),
                }],
            }],
            browser.json)

    @browsing
    def test_dossier_navigation_for_dossier_templates(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(self.dossiertemplate, view='dossier_navigation.json')
        self.assertEqual(
            [{
                "text": self.dossiertemplate.Title(),
                "description": self.dossiertemplate.Description(),
                "uid": IUUID(self.dossiertemplate),
                "url": self.dossiertemplate.absolute_url(),
                "nodes": [{
                    "text": self.subdossiertemplate.Title(),
                    "description": self.subdossiertemplate.Description(),
                    "nodes": [],
                    "uid": IUUID(self.subdossiertemplate),
                    "url": self.subdossiertemplate.absolute_url(),
                }],
            }],
            browser.json)

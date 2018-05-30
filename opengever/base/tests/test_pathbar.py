from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestPathBar(IntegrationTestCase):

    @browsing
    def test_first_part_is_admin_unit_title_if_multiple_admin_units(self, browser):
        self.login(self.regular_user, browser)
        create(Builder('admin_unit')
               .having(title=u'Nebenmandant',
                       unit_id=u'plonez',
                       public_url='http://nohost/plonez'))

        browser.open(self.dossier)
        first_part = browser.css('#portal-breadcrumbs li a')[0]
        self.assertEquals('Hauptmandant', first_part.text)
        self.assertEquals(self.portal.absolute_url(), first_part.get('href'))


    @browsing
    def test_contains_contenttype_icon_class(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document)

        self.assertEquals(
            ['contenttype-opengever-repository-repositoryfolder',
             'contenttype-opengever-repository-repositoryfolder',
             'contenttype-opengever-repository-repositoryroot',
             'contenttype-opengever-dossier-businesscasedossier',
             'contenttype-opengever-document-document'],
            [crumb.get('class') for crumb in
             browser.css('#portal-breadcrumbs li a i')])

    @browsing
    def test_repositories_are_grouped_in_a_sublist(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)

        self.assertEquals(
            [u'1.1. Vertr\xe4ge und Vereinbarungen',
             u'1. F\xfchrung',
             u'Ordnungssystem',
             u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'],
            browser.css('#portal-breadcrumbs li a').text)

        self.assertEquals([u'1. F\xfchrung', 'Ordnungssystem'],
                          browser.css('#portal-breadcrumbs li ul a').text)

    @browsing
    def test_last_part_is_linked(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)

        last_link = browser.css('#portal-breadcrumbs a')[-1]
        self.assertEqual(self.dossier.absolute_url(),
                         last_link.node.attrib['href'])

    @browsing
    def test_proposal_is_linked_with_title(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.proposal)

        last_link = browser.css('#portal-breadcrumbs a')[-1]
        self.assertEqual(self.proposal.absolute_url(),
                         last_link.node.attrib['href'])
        self.assertEqual(self.proposal.title, last_link.text)

    @browsing
    def test_meeting_is_linked_with_title(self, browser):
        self.activate_feature('meeting')

        self.login(self.meeting_user, browser)
        browser.open(self.meeting)

        last_link = browser.css('#portal-breadcrumbs a')[-1]
        self.assertEqual(
            'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/meeting-1',
            last_link.get('href'))

        self.assertEqual(self.meeting.get_title(), last_link.text)

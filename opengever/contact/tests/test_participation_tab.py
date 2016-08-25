from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class ParticipationTab(FunctionalTestCase):

    def setUp(self):
        super(ParticipationTab, self).setUp()
        create(Builder('contactfolder'))
        self.dossier = create(Builder('dossier'))
        self.hans = create(Builder('person').having(
            firstname=u'Hans', lastname=u'M\xfcller'))
        self.sandra = create(Builder('person').having(
            firstname=u'sandra', lastname=u'Meier'))
        self.peter_ag = create(Builder('organization')
                               .having(name=u'Peter AG'))

        create(Builder('participation')
               .for_contact(self.hans)
               .for_dossier(self.dossier)
               .with_roles(['regard', 'final-drawing']))
        create(Builder('participation')
               .for_contact(self.peter_ag)
               .for_dossier(self.dossier)
               .with_roles(['participation']))

    @browsing
    def test_list_all_participating_contacts_and_link_them_to_detail_view(self, browser):
        browser.login().open(self.dossier,
                             view=u'tabbedview_view-participations')

        self.assertEquals(
            [u'Hans M\xfcller', 'Peter AG'],
            browser.css('#participation_listing .contact').text)

        links = browser.css('#participation_listing .contact a')
        self.assertEquals(
            [self.hans.get_url(), self.peter_ag.get_url()],
            [link.get('href') for link in links])

        self.assertEquals(
            ['contenttype-person', 'contenttype-organization'],
            [link.get('class') for link in links])

    @browsing
    def test_list_only_participations_of_the_current_dossier(self, browser):
        dossier_2 = create(Builder('dossier'))
        create(Builder('participation')
               .for_contact(self.sandra)
               .for_dossier(dossier_2)
               .with_roles(['regard, final-drawing']))

        browser.login().open(self.dossier,
                             view=u'tabbedview_view-participations')
        self.assertEquals(
            [u'Hans M\xfcller', 'Peter AG'],
            browser.css('#participation_listing .contact').text)

    @browsing
    def test_roles_of_each_participation_is_visible_and_translated(self, browser):
        browser.login().open(self.dossier,
                             view=u'tabbedview_view-participations')

        row1, row2 = browser.css('#participation_listing > li')

        self.assertEquals([u'Hans M\xfcller'], row1.css('.contact').text)
        self.assertEquals(['Regard', 'Final drawing'], row1.css('.roles li').text)

        self.assertEquals([u'Peter AG'], row2.css('.contact').text)
        self.assertEquals(['Participation'], row2.css('.roles li').text)

    @browsing
    def test_edit_action_is_available(self, browser):
        browser.login().open(self.dossier,
                             view=u'tabbedview_view-participations')

        edit_link = browser.css('#participation_listing > li .edit-action').first

        self.assertEquals('Edit', edit_link.text)
        self.assertEquals('http://nohost/plone/dossier-1/participation-1/edit',
                          edit_link.get('href'))

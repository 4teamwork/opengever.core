from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.dossier.dossiertemplate.behaviors import IRestrictAddableDossierTemplates
from opengever.testing import FunctionalTestCase


class TestRestrictAddableDossierTemplatesBehavior(FunctionalTestCase):

    def setUp(self):
        super(TestRestrictAddableDossierTemplatesBehavior, self).setUp()
        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository')
                                 .having(title_de=u'Anfragen',
                                         title_fr=u'Demandes',
                                         title_en=u'Requests')
                                 .within(self.root))
        self.templatefolder = create(Builder('templatefolder'))

        self.grant('Editor', 'Contributor', 'Administrator')

    @browsing
    def test_only_templatedossiers_are_selectable(self, browser):
        doc = create(Builder('document').within(self.templatefolder))
        dossiertemplate = create(Builder('dossiertemplate')
                                 .within(self.templatefolder))

        browser.login().open(self.repository, view='edit')
        browser.fill({'Addable dossier templates': [doc]})
        browser.click_on('Save')
        self.assertEquals(
            [],
            IRestrictAddableDossierTemplates(self.repository).addable_dossier_templates)

        browser.login().open(self.repository, view='edit')
        browser.fill({'Addable dossier templates': [dossiertemplate]})
        browser.click_on('Save')
        relations = IRestrictAddableDossierTemplates(self.repository).addable_dossier_templates
        self.assertEquals([dossiertemplate],
                          [rel.to_object for rel in relations])

    @browsing
    def test_only_main_templatedossiers_are_selectable(self, browser):
        dossiertemplate = create(Builder('dossiertemplate')
                                 .within(self.templatefolder))
        sub_dossiertemplate = create(Builder('dossiertemplate')
                                     .within(dossiertemplate))

        browser.login().open(self.repository, view='edit')
        browser.fill({'Addable dossier templates': [sub_dossiertemplate]})
        browser.click_on('Save')

        relations = IRestrictAddableDossierTemplates(self.repository).addable_dossier_templates
        self.assertEquals([], relations)

        browser.login().open(self.repository, view='edit')
        browser.fill({'Addable dossier templates': [dossiertemplate]})
        browser.click_on('Save')

        relations = IRestrictAddableDossierTemplates(self.repository).addable_dossier_templates
        self.assertEquals([dossiertemplate],
                          [rel.to_object for rel in relations])

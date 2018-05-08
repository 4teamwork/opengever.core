# -*- coding: utf-8 -*-
from plone import api
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import IntegrationTestCase
from zope.annotation.interfaces import IAnnotations


class TestCreateDocFromOneoffixxTemplate(IntegrationTestCase):

    def setUp(self):
        super(TestCreateDocFromOneoffixxTemplate, self).setUp()
        self.activate_feature("officeconnector-checkout")
        self.activate_feature("oneoffixx")

    @browsing
    def test_document_creation_from_oneoffixx_template_creates_shadow_doc(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        factoriesmenu.add('document_with_oneoffixx_template')

        node = browser.css("#form-widgets-template-2574d08d-95ea-4639-beab-3103fe4c3bc7").first
        browser.fill({'Title': 'A doc'})
        browser.fill({'Template': node.get("title")})
        browser.find('Save').click()

        self.assertEqual('document-state-shadow',
                         api.content.get_state(browser.context))
        self.assertTrue(browser.context.is_shadow_document())

    @browsing
    def test_retry_button_visible_on_shadow_doc(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        factoriesmenu.add('document_with_oneoffixx_template')
        node = browser.css("#form-widgets-template-2574d08d-95ea-4639-beab-3103fe4c3bc7").first
        browser.fill({'Title': 'A doc'})
        browser.fill({'Template': node.get("title")})
        browser.find('Save').click()
        browser.open(browser.context, view='tabbedview_view-overview')
        self.assertEqual(['Oneoffixx retry'], browser.css('a.oc-checkout').text)

    @browsing
    def test_template_id_stored_in_annotations(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        factoriesmenu.add('document_with_oneoffixx_template')

        node = browser.css("#form-widgets-template-2574d08d-95ea-4639-beab-3103fe4c3bc7").first
        browser.fill({'Title': 'A doc'})
        browser.fill({'Template': node.get("title")})
        browser.find('Save').click()

        annotations = IAnnotations(browser.context)
        self.assertEqual(node.get("value"), annotations['template-id'])


class TestOneOffixxTemplateFeature(IntegrationTestCase):

    @browsing
    def test_doc_from_oneoffixx_template_available_if_oneoffixxtemplate_feature_enabled(self, browser):
        self.activate_feature("officeconnector-checkout")
        self.login(self.manager, browser)
        browser.open(self.dossier)

        self.assertEquals(
            ['Document',
             'document_with_template',
             'Task',
             'Add task from template',
             'Subdossier',
             'Participant'],
            factoriesmenu.addable_types())

        self.activate_feature("oneoffixx")
        browser.open(self.dossier)
        self.assertEquals(
            ['Document',
             'document_with_template',
             'document_with_oneoffixx_template',
             'Task',
             'Add task from template',
             'Subdossier',
             'Participant'],
            factoriesmenu.addable_types())

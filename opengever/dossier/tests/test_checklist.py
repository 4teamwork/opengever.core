from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplate
from opengever.testing import IntegrationTestCase
import json


class TestPatchDossierChecklistViaApi(IntegrationTestCase):

    def setUp(self):
        super(TestPatchDossierChecklistViaApi, self).setUp()
        self.checklist_interface = IDossier
        with self.login(self.dossier_responsible):
            self.obj = self.dossier

    def assert_checklist_is_valid(self, browser, checklist):
        browser.open(self.obj,
                     data=json.dumps({'checklist': checklist}),
                     method='PATCH', headers=self.api_headers)

        self.assertEqual(204, browser.status_code)
        self.assertEqual(checklist, self.checklist_interface(self.obj).checklist)

    def assert_checklist_is_invalid(self, browser, checklist):
        with browser.expect_http_error(400):
            browser.open(self.obj,
                         data=json.dumps({'checklist': checklist}),
                         method='PATCH', headers=self.api_headers)

        self.assertIn('ValidationError', browser.json['message'])

    @browsing
    def test_checklist_field_is_valid(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        checklist = {
            u'items': [{u'title': u'St\xe4p 1', u'state': u'open'}]
        }
        self.assert_checklist_is_valid(browser, checklist)

    @browsing
    def test_checklist_field_with_multiple_items_is_valid(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        checklist = {
            u'items': [{u'title': u'Step 1', u'state': u'open'},
                       {u'title': u'Step 2', u'state': u'closed'}]
        }
        self.assert_checklist_is_valid(browser, checklist)

    @browsing
    def test_checklist_field_with_empty_items_list_is_valid(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        checklist = {
            u'items': []
        }
        self.assert_checklist_is_valid(browser, checklist)

    @browsing
    def test_checklist_is_invalid_if_items_is_not_an_array(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        checklist = {
            u'items': u'invalid'
        }
        self.assert_checklist_is_invalid(browser, checklist)

    @browsing
    def test_checklist_is_invalid_if_title_is_missing(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        checklist = {
            u'items': [{u'state': u'open'}]
        }
        self.assert_checklist_is_invalid(browser, checklist)

    @browsing
    def test_checklist_is_invalid_if_title_is_not_a_string(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        checklist = {
            u'items': [{u'title': 12, u'state': u'open'}]
        }
        self.assert_checklist_is_invalid(browser, checklist)

    @browsing
    def test_checklist_is_invalid_if_state_is_missing(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        checklist = {
            u'items': [{u'title': u'Step 1'}]
        }
        self.assert_checklist_is_invalid(browser, checklist)

    @browsing
    def test_checklist_is_invalid_if_state_is_invalid(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        checklist = {
            u'items': [{u'title': u'Step 1', u'state': u'invalid'}]
        }
        self.assert_checklist_is_invalid(browser, checklist)

    @browsing
    def test_checklist_is_invalid_if_additional_keys_are_set(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        checklist_1 = {
            u'items': [{u'title': u'Step 1', u'state': u'open', u'info': u'An information'}]
        }
        self.assert_checklist_is_invalid(browser, checklist_1)
        checklist_2 = {
            u'items': [{u'title': u'Step 1', u'state': u'open'}],
            u'items_total': 1,
        }
        self.assert_checklist_is_invalid(browser, checklist_2)


class TestPatchDossierChecklistTTW(TestPatchDossierChecklistViaApi):

    def assert_checklist_is_valid(self, browser, checklist):
        browser.visit(self.obj, view='edit')
        browser.fill({'Checklist': json.dumps(checklist)})
        browser.find('Save').click()

        self.assertEqual(checklist, self.checklist_interface(self.obj).checklist)

    def assert_checklist_is_invalid(self, browser, checklist):
        browser.visit(self.obj, view='edit')
        browser.fill({'Checklist': json.dumps(checklist)})
        browser.find('Save').click()
        self.assertEqual(['There were some errors.'], error_messages())
        self.assertIn('Checklist', browser.css('div.error').text[0])


class TestPatchDossierTemplateChecklistViaApi(TestPatchDossierChecklistViaApi):

    def setUp(self):
        super(TestPatchDossierTemplateChecklistViaApi, self).setUp()
        self.checklist_interface = IDossierTemplate
        with self.login(self.dossier_responsible):
            self.obj = self.dossiertemplate


class TestPatchDossierTemplateChecklistTTW(TestPatchDossierChecklistTTW):

    def setUp(self):
        super(TestPatchDossierTemplateChecklistTTW, self).setUp()
        self.checklist_interface = IDossierTemplate
        with self.login(self.dossier_responsible):
            self.obj = self.dossiertemplate

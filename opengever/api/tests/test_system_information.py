from ftw.testbrowser import browsing
from opengever.dossier.interfaces import IDossierParticipants
from opengever.testing import IntegrationTestCase
from plone import api


class TestSystemInformation(IntegrationTestCase):

    @browsing
    def test_provided_information_keys(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal.absolute_url() + '/@system-information', headers=self.api_headers)

        self.assertEqual(browser.status_code, 200)
        self.assertEqual([
            u'dossier_participation_roles',
            u'property_sheets',
        ], sorted(browser.json.keys()))

    @browsing
    def test_dossier_participation_roles(self, browser):
        self.login(self.manager, browser)
        api.portal.set_registry_record('primary_participation_roles', ['regard'], IDossierParticipants)

        self.login(self.regular_user, browser)
        browser.open(self.portal.absolute_url() + '/@system-information', headers=self.api_headers)

        self.assertEqual([
            {u'active': True, u'token': u'final-drawing', u'primary': False, u'title': u'Final signature'},
            {u'active': True, u'token': u'regard', u'primary': True, u'title': u'For your information'},
            {u'active': True, u'token': u'participation', u'primary': False, u'title': u'Participation'}
        ], browser.json.get('dossier_participation_roles'))

    @browsing
    def test_property_sheets(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal.absolute_url() + '/@system-information', headers=self.api_headers)

        self.assertEqual(
            [u'dossier_default', u'schema1', u'schema2'],
            sorted(browser.json.get('property_sheets').keys()))

        self.assertEqual(
            {
                u'assignments': [
                    {
                        u'id': u'IDocumentMetadata.document_type.directive',
                        u'title': u'Document (Type: Directive)'
                    }
                ],
                u'fields': [
                    {
                        u'available_as_docproperty': False,
                        u'description': u'',
                        u'field_type': u'textline',
                        u'name': u'textline',
                        u'required': False,
                        u'title': u'A line of text'
                    }
                ],
                u'id': u'schema2'
            },
            browser.json.get('property_sheets').get('schema2'))

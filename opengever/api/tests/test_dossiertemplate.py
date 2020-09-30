from ftw.testbrowser import browsing
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplate
from opengever.testing import IntegrationTestCase
import json


class TestDossierTemplateSerialization(IntegrationTestCase):

    features = ('dossiertemplate', )

    @browsing
    def test_dossier_template_serializer(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossiertemplate, headers=self.api_headers)

        self.assertEqual(browser.status_code, 200)
        self.assertEqual(browser.json[u'@id'],
                         self.dossiertemplate.absolute_url())
        self.assertEqual(browser.json[u'@type'],
                         u'opengever.dossier.dossiertemplate')
        self.assertEqual(browser.json[u'title'],
                         self.dossiertemplate.title)
        self.assertEqual(browser.json[u'title_help'],
                         self.dossiertemplate.title_help)
        self.assertEqual(
            browser.json[u'keywords'],
            [{u'title': u'secret', u'token': u'secret'},
             {u'title': u'special', u'token': u'special'}]
             )
        self.assertEqual(browser.json[u'filing_prefix'],
                         {u'title': u'Department', u'token': u'department'})


class TestDossierTemplatePost(IntegrationTestCase):

    features = ('dossiertemplate', )

    @browsing
    def test_creating_dossiertemplate_is_forbidden_for_regular_users(self, browser):
        data = {
            '@type': 'opengever.dossier.dossiertemplate',
            'title': 'New dossier template',
        }

        self.login(self.regular_user, browser)
        with browser.expect_unauthorized():
            browser.open(self.templates, data=json.dumps(data),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'message': u'You are not authorized to access this resource.',
             u'type': u'Unauthorized'},
            browser.json
            )

    @browsing
    def test_creating_dossiertemplate(self, browser):
        self.login(self.administrator, browser)
        data = {
            '@type': 'opengever.dossier.dossiertemplate',
            'title': 'New dossier template',
            'title_help': 'My title help',
            'predefined_keywords': True,
            'restrict_keywords': True,
            'keywords': ['first', 'second'],
            'comments': 'A comment',
            'filing_prefix': 'department'
        }

        with self.observe_children(self.templates) as children:
            browser.open(self.templates, data=json.dumps(data),
                         method='POST', headers=self.api_headers)

        self.assertEqual(201, browser.status_code)
        self.assertEqual(1, len(children['added']))
        template = children['added'].pop()

        self.assertEqual(browser.json['@id'], template.absolute_url())
        self.assertEqual('New dossier template', template.Title())
        self.assertEqual('My title help', template.title_help)
        self.assertTrue(template.predefined_keywords)
        self.assertTrue(template.restrict_keywords)
        self.assertItemsEqual('A comment', IDossierTemplate(template).comments)
        self.assertItemsEqual(
            ('first', 'second'), IDossierTemplate(template).keywords)
        self.assertItemsEqual(
            'department', IDossierTemplate(template).filing_prefix)


class TestDossierTemplatePatch(IntegrationTestCase):

    features = ('dossiertemplate', )

    @browsing
    def test_patching_dossiertemplate_is_forbidden_for_regular_users(self, browser):
        data = {'title': 'New dossier template'}

        self.login(self.regular_user, browser)
        with browser.expect_unauthorized():
            browser.open(self.dossiertemplate, data=json.dumps(data),
                         method='PATCH', headers=self.api_headers)

        self.assertEqual(
            {u'message': u'You are not authorized to access this resource.',
             u'type': u'Unauthorized'},
            browser.json
            )

    @browsing
    def test_dossier_template_patch(self, browser):
        self.login(self.administrator, browser)
        self.assertEqual('Bauvorhaben klein', self.dossiertemplate.Title())

        data = {'title': 'New title'}
        browser.open(self.dossiertemplate.absolute_url(), data=json.dumps(data),
                     method='PATCH', headers=self.api_headers)

        self.assertEqual(204, browser.status_code)
        self.assertEqual('New title', self.dossiertemplate.Title())


class TestDossierTemplateDelete(IntegrationTestCase):

    features = ('dossiertemplate', )

    @browsing
    def test_deleting_dossiertemplate_is_forbidden_for_regular_users(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_unauthorized():
            browser.open(self.dossiertemplate, method='DELETE',
                         headers=self.api_headers)

        self.assertEqual(
            {u'message': u'You are not authorized to access this resource.',
             u'type': u'Unauthorized'},
            browser.json
            )

    @browsing
    def test_dossiertemplate_delete(self, browser):
        self.login(self.administrator, browser)
        with self.observe_children(self.templates) as children:
            browser.open(self.dossiertemplate.absolute_url(),
                         method='DELETE', headers=self.api_headers)

        self.assertEqual(204, browser.status_code)
        self.assertEqual(1, len(children['removed']))

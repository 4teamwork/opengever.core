from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_OFFICEATWORK_LAYER
from opengever.testing import FunctionalTestCase
from zExceptions import Unauthorized
import json


class TestCreateWithOfficeatworkFeatureDisabled(FunctionalTestCase):

    def setUp(self):
        super(TestCreateWithOfficeatworkFeatureDisabled, self).setUp()
        self.dossier = create(Builder('dossier'))

    @browsing
    def test_create_view_unavailable(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .as_shadow_document())
        # XXX This causes an infinite redirection loop between ++add++ and
        # reqiure_login. By enabling exception_bubbling we can catch the
        # Unauthorized exception and end the infinite loop.
        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized):
        # with browser.expect_unauthorized():
            browser.login().open(document, view='create_with_officeatwork')


class TestCreateWithOfficeatwork(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_OFFICEATWORK_LAYER

    def setUp(self):
        super(TestCreateWithOfficeatwork, self).setUp()
        self.dossier = create(Builder('dossier'))

    @browsing
    def test_create_with_officeatwork_downloads_ocm_file(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .as_shadow_document())
        browser.login().open(document, view='create_with_officeatwork')

        self.assertEqual('attachment; filename="document-1.ocm"',
                         browser.headers['content-disposition'])
        self.assertEqual('application/x-officeconnector',
                         browser.headers['content-type'])

        # separately validate basic auth data
        ocm_content = json.loads(browser.contents)
        self.assertIn('auth', ocm_content)
        auth = ocm_content.pop('auth')
        self.assertTrue(auth.startswith(u'Basic'),
                        'ocm file should contain basic auth information')

        self.assertEqual(
            {'action': 'officeatwork',
             'cookie': '',
             'document': {
                'metadata': {},
                'title': u'Testdokum\xe4nt',
                'url': 'http://nohost/plone/dossier-1/document-1'}},
            ocm_content
        )

    @browsing
    def test_document_in_non_shadow_state_raises_unauthorized(self, browser):
        document = create(Builder('document').within(self.dossier))
        # XXX This causes an infinite redirection loop between ++add++ and
        # reqiure_login. By enabling exception_bubbling we can catch the
        # Unauthorized exception and end the infinite loop.
        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized):
        # with browser.expect_unauthorized():
            browser.login().open(document, view='create_with_officeatwork')

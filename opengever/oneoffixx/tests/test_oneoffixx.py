from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.oneoffixx.exceptions import OneoffixxBackendException
from opengever.oneoffixx.interfaces import IOneoffixxSettings
from opengever.oneoffixx.tests import BaseOneOffixxTestCase
from opengever.oneoffixx.utils import whitelisted_template_types
from opengever.testing import IntegrationTestCase
from plone import api
from urlparse import parse_qs
from zope.annotation.interfaces import IAnnotations
import json
import requests
import requests_mock


class TestCreateDocFromOneoffixxTemplate(BaseOneOffixxTestCase):

    @browsing
    def test_document_creation_from_oneoffixx_template_creates_shadow_doc(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Document from Primedocs template')

        browser.fill({'Title': 'A doc'})
        browser.find('Save').click()

        document = browser.context
        self.assertEqual(
            'document-state-shadow', api.content.get_state(document))
        self.assertTrue(document.is_shadow_document())
        self.assertEqual('A doc', document.title)

    @browsing
    def test_retry_button_visible_on_shadow_doc(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Document from Primedocs template')

        browser.fill({'Title': 'A doc'})
        browser.find('Save').click()
        browser.open(browser.context, view='tabbedview_view-overview')
        self.assertEqual(['Retry with Primedocs'], browser.css('a.oc-checkout').text)

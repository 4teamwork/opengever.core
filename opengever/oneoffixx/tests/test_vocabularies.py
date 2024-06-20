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


class TestOneOffixxFileTypesVocabulary(BaseOneOffixxTestCase):

    @browsing
    def test_oneoffixx_filetype_vocabulary_represents_registry_setting(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.portal, view="@vocabularies/opengever.oneoffixx.filetypes", headers=self.api_headers)

        self.assertEqual(
            [{u'token': u'GeverWord', u'title': u'Word'},
             {u'token': u'GeverExcel', u'title': u'Excel'},
             {u'token': u'GeverPowerpoint', u'title': u'Powerpoint'}],
             browser.json['items'])

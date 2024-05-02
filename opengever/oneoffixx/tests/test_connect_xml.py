from ftw.testbrowser import browsing
from ftw.testing import freeze
from lxml import etree
from opengever.officeconnector.testing import FREEZE_DATE
from opengever.oneoffixx.interfaces import IOneoffixxSettings
from opengever.testing import IntegrationTestCase
from pkg_resources import resource_string
from plone import api


class TestConnectXML(IntegrationTestCase):
    features = ("officeconnector-checkout", "oneoffixx")

    @browsing
    def test_connect_xml_view_returns_xml_for_doc_created_from_oneoffixx(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.shadow_document, view="oneoffix_connect_xml")
        xml = etree.fromstring(browser.contents)

        namespace = "http://schema.oneoffixx.com/OneOffixxConnectBatch/1"
        self.assertEqual("{%s}OneOffixxConnectBatch" % namespace, xml.tag)

    @browsing
    def test_connect_xml_content(self, browser):
        self.login(self.dossier_responsible, browser)

        api.portal.set_registry_record(interface=IOneoffixxSettings, name='template_filter_tag', value=u'Gever')

        # Freezing the JWT embedded in the XML file to the OC testing standard
        with freeze(FREEZE_DATE):
            browser.open(self.shadow_document, view="oneoffix_connect_xml")

        expected_oneoffixx_xml = resource_string("opengever.oneoffixx.tests.assets", "oneoffixx_connect_xml.txt")

        self.maxDiff = None
        self.assertEqual(expected_oneoffixx_xml.splitlines(), browser.contents.splitlines())
        self.assertEqual("application/xml", browser.headers.get('Content-type'))

    @browsing
    def test_connect_xml_view_allowed_only_on_documents_in_shadow_state(self, browser):
        self.login(self.manager, browser)
        with browser.expect_http_error(404):
            browser.open(self.document, view="oneoffix_connect_xml")

        self.document.as_shadow_document()
        browser.open(self.document, view="oneoffix_connect_xml")

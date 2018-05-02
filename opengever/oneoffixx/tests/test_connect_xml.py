from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from lxml import etree
from opengever.testing import IntegrationTestCase
from pkg_resources import resource_string


class TestConnectXML(IntegrationTestCase):
    features = ("officeconnector-checkout", "oneoffixx")

    def create_document(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        factoriesmenu.add('document_with_oneoffixx_template')

        node = browser.css("#form-widgets-template-2574d08d-95ea-4639-beab-3103fe4c3bc7").first
        browser.fill({'Title': 'A doc'})
        browser.fill({'Template': node.get("title")})
        browser.find('Save').click()
        return browser.context

    @browsing
    def test_connect_xml_view_returns_xml_for_doc_created_from_oneoffixx(self, browser):
        document = self.create_document(browser)
        browser.open(document, view="oneoffix_connect_xml")
        xml = etree.fromstring(browser.contents)

        namespace = "http://schema.oneoffixx.com/OneOffixxConnectBatch/1"
        self.assertEqual("{%s}OneOffixxConnectBatch" % namespace, xml.tag)

        templateid_tag = xml.find(".//{%s}TemplateId" % namespace)
        self.assertEqual('2574d08d-95ea-4639-beab-3103fe4c3bc7',
                         templateid_tag.text)

    @browsing
    def test_connect_xml_content(self, browser):
        document = self.create_document(browser)
        browser.open(document, view="oneoffix_connect_xml")

        xml = resource_string("opengever.oneoffixx.tests.assets", "oneoffixx_connect_xml.txt")
        self.assertEqual(xml, browser.contents)

        self.assertEqual("application/xml", browser.headers["Content-type"])

    @browsing
    def test_connect_xml_view_allowed_only_on_documents_in_shadow_state(self, browser):
        self.login(self.manager, browser)
        with browser.expect_http_error(404):
            browser.open(self.document, view="oneoffix_connect_xml")

        self.document.as_shadow_document()
        browser.open(self.document, view="oneoffix_connect_xml")

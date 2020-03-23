from ftw import bumblebee
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.wopi import discovery
from opengever.wopi.interfaces import IWOPISettings
from plone.protect import createToken
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TestDocumentTooltip(IntegrationTestCase):
    """Test the lazy loading document tooltip."""

    features = ('!officeconnector-attach', '!officeconnector-checkout')

    @browsing
    def test_tooltip_contains_linked_breadcrumb(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tooltip')

        chain = [self.repository_root, self.branch_repofolder,
                 self.leaf_repofolder, self.dossier, self.document]

        self.assertEquals(
            [obj.Title().decode('utf-8') for obj in chain],
            browser.css('.tooltip-breadcrumb li').text)

        self.assertEquals(
            [obj.absolute_url() for obj in chain],
            [link.get('href')
             for link in browser.css('.tooltip-breadcrumb li a')])

    @browsing
    def test_tooltip_actions(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tooltip')
        metadata, checkout, download, details = browser.css(
            '.file-action-buttons a')

        # metadata
        self.assertEquals('Edit metadata', metadata.text)
        self.assertEquals(
            'http://nohost/plone/ordnungssystem/fuhrung'
            '/vertrage-und-vereinbarungen/dossier-1/document-14'
            '/edit_checker',
            metadata.get('href'))

        # checkout and edit
        self.assertEquals('Checkout and edit', checkout.text)
        self.assertTrue(checkout.get('href').startswith(
            'http://nohost/plone/ordnungssystem/fuhrung'
            '/vertrage-und-vereinbarungen/dossier-1/document-14'
            '/editing_document?_authenticator='
        ))

        # download copy
        self.assertEquals('Download copy', download.text)
        self.assertTrue(download.get('href').startswith(
            'http://nohost/plone/ordnungssystem/fuhrung'
            '/vertrage-und-vereinbarungen/dossier-1/document-14'
            '/file_download_confirmation?_authenticator='))

        # link to details
        self.assertEquals('Open detail view', details.text)
        self.assertEquals(
            'http://nohost/plone/ordnungssystem/fuhrung'
            '/vertrage-und-vereinbarungen/dossier-1/document-14',
            details.get('href'))

    @browsing
    def test_tooltip_actions_with_office_online_enabled(self, browser):
        self.login(self.regular_user, browser)

        # Enable WOPI / Office Online support
        settings = getUtility(IRegistry).forInterface(IWOPISettings)
        settings.enabled = True
        settings.discovery_url = u'http://localhost/hosting/discovery'

        discovery._EDITABLE_EXTENSIONS = {
            'http://localhost/hosting/discovery': set(['docx', 'xlsx', 'pptx'])
        }

        browser.open(self.document, view='tooltip')
        metadata, checkout, edit_in_office_online, download, details = browser.css(
            '.file-action-buttons a')

        self.assertEquals('Edit metadata', metadata.text)
        self.assertEquals('Checkout and edit', checkout.text)

        self.assertEquals('Edit in Office Online', edit_in_office_online.text)
        self.assertTrue(edit_in_office_online.get('href').startswith(
            'http://nohost/plone/ordnungssystem/fuhrung'
            '/vertrage-und-vereinbarungen/dossier-1/document-14'
            '/office_online_edit'
        ))

        self.assertEquals('Download copy', download.text)
        self.assertEquals('Open detail view', details.text)

    @browsing
    def test_checkout_link_is_only_available_for_documents(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tooltip')
        self.assertIn('Checkout and edit',
                      browser.css('.file-action-buttons a').text)

        browser.open(self.mail_eml, view='tooltip')
        self.assertNotIn('Checkout and edit',
                         browser.css('.file-action-buttons a').text)

        browser.open(self.mail_msg, view='tooltip')
        self.assertNotIn('Checkout and edit',
                         browser.css('.file-action-buttons a').text)

    @browsing
    def test_checkout_link_is_only_available_for_editable_docs(self, browser):
        self.login(self.secretariat_user, browser)

        browser.open(self.resolvable_dossier,
                     view='transition-resolve',
                     data={'_authenticator': createToken()})

        browser.open(self.resolvable_document, view='tooltip')
        self.assertEquals(['Download copy',
                           'Open detail view'],
                          browser.css('.file-action-buttons a').text)

    @browsing
    def test_download_link_is_available_for_documents_and_mails_when_file_exists(self, browser):  # noqa
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tooltip')
        self.assertIn(
            'Download copy', browser.css('.file-action-buttons a').text)

        browser.open(self.mail_eml, view='tooltip')
        self.assertIn(
            'Download copy', browser.css('.file-action-buttons a').text)

        browser.open(self.mail_msg, view='tooltip')
        self.assertIn(
            'Download copy', browser.css('.file-action-buttons a').text)

        browser.open(self.empty_document, view='tooltip')
        self.assertNotIn(
            'Download copy', browser.css('.file-action-buttons a').text)

    @browsing
    def test_download_link_redirects_to_orginal_message_when_exists(self, browser):  # noqa
        self.login(self.regular_user, browser)

        browser.open(self.mail_msg, view='tooltip')

        self.assertTrue(
            browser.find('Download copy').get('href').startswith(
                'http://nohost/plone/ordnungssystem/fuhrung'
                '/vertrage-und-vereinbarungen/dossier-1/document-30'
                '/@@download/original_message?'
            ))


class TestDocumentLinkWidgetWithActivatedBumblebee(IntegrationTestCase):
    """Test document link widget interactions with Bumblebee."""

    features = ('bumblebee', )

    @browsing
    def test_tooltip_contains_preview_thumbnail(self, browser):
        self.login(self.regular_user, browser)

        self.request.form['bid'] = 'THEBID'
        thumbnail_url = bumblebee.get_service_v3().get_representation_url(
            self.document, 'thumbnail')
        del self.request.form['bid']

        browser.open(self.document, {'bid': 'THEBID'}, view='tooltip')

        self.assertEquals(
            thumbnail_url,
            browser.css('.preview img').first.get('src'))

        self.assertEquals(
            ['Open document preview'],
            browser.css('.preview span').text)

# -*- coding: utf-8 -*-
from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from ftw.testing import freeze
from ooxml_docprops import read_properties
from opengever.contact.interfaces import IContactSettings
from opengever.dossier.docprops import TemporaryDocFile
from opengever.dossier.interfaces import ITemplateFolderProperties
from opengever.dossier.templatefolder import get_template_folder
from opengever.dossier.templatefolder.interfaces import ITemplateFolder
from opengever.dossier.tests import OGDS_USER_ATTRIBUTES
from opengever.journal.handlers import DOC_PROPERTIES_UPDATED
from opengever.journal.tests.utils import get_journal_entry
from opengever.ogds.base.actor import Actor
from opengever.testing import add_languages
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import get_contacts_token
from opengever.testing.pages import sharing_tab_data
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from unittest import skip
from zope.app.intid.interfaces import IIntIds
from zope.component import getMultiAdapter
from zope.component import getUtility


class TestDocumentWithTemplateFormPlain(IntegrationTestCase):

    @browsing
    def test_form_lists_all_templates_alphabetically_including_nested(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='document_with_template')

        expected_listing = [
            {'': '', 'Creator': 'nicole.kohler', 'Modified': '28.12.2010', 'Title': u'T\xc3\xb6mpl\xc3\xb6te Mit'},
            {'': '', 'Creator': 'nicole.kohler', 'Modified': '31.08.2016', 'Title': u'T\xc3\xb6mpl\xc3\xb6te Normal'},
            {'': '', 'Creator': 'nicole.kohler', 'Modified': '31.08.2016', 'Title': u'T\xc3\xb6mpl\xc3\xb6te Ohne'},
            {'': '', 'Creator': 'nicole.kohler', 'Modified': '29.02.2020', 'Title': u'T\xc3\xb6mpl\xc3\xb6te Sub'},
            ]

        self.assertEquals(expected_listing, browser.css('table.listing').first.dicts())

    @browsing
    def test_form_does_not_inlcude_participants_with_disabled_feature(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='document_with_template')

        # XXX - The CheckBoxWidget is rendered with two labels (only in testing).
        # The reason for that is a wrong widget renderer adapter lookup because
        # of the stacked globalregistry (see plone.testing.zca: pushGlobalRegistry
        # for more information).
        expected_labels = [
            u'Template',
            u'Filter',
            u'Title',
            u'Edit after creation',
            ]

        self.assertEqual(expected_labels, browser.css('#form label').text)

    @browsing
    def test_cancel_redirects_to_the_dossier(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='document_with_template')

        browser.find('Cancel').click()

        self.assertEquals(self.dossier, browser.context)
        self.assertEquals('tabbed_view', plone.view())

    @browsing
    def test_save_redirects_to_the_dossiers_document_tab(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='document_with_template')

        browser.fill({
            'form.widgets.template': str(getUtility(IIntIds).getId(self.normal_template)),
            'Title': 'Test Document',
            'Edit after creation': False,
            }).save()

        self.assertEquals(self.dossier, browser.context)
        self.assertEquals(self.dossier.absolute_url() + '#documents', browser.url)

    @browsing
    def test_new_document_is_titled_with_the_form_value(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='document_with_template')
        browser.fill({
            'form.widgets.template': str(getUtility(IIntIds).getId(self.normal_template)),
            'Title': 'Test Document',
            }).save()

        document = self.dossier.listFolderContents()[-1]
        self.assertEquals('Test Document', document.title)

    @browsing
    def test_new_document_values_are_filled_with_default_values(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='document_with_template')
        browser.fill({
            'form.widgets.template': str(getUtility(IIntIds).getId(self.normal_template)),
            'Title': 'Test Document',
            }).save()

        document = self.dossier.listFolderContents()[-1]
        self.assertEquals(date.today(), document.document_date)
        self.assertEquals(u'privacy_layer_no', document.privacy_layer)

    @browsing
    def test_file_of_the_new_document_is_a_copy_of_the_template(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='document_with_template')
        browser.fill({
            'form.widgets.template': str(getUtility(IIntIds).getId(self.normal_template)),
            'Title': 'Test Document',
            }).save()

        document = self.dossier.listFolderContents()[-1]

        self.assertEquals(self.normal_template.file.data, document.file.data)
        self.assertNotEquals(self.normal_template.file, document.file)

    @browsing
    def test_doc_properties_are_not_created_when_disabled(self, browser):
        self.login(self.regular_user, browser)

        with freeze(datetime(2020, 10, 28, 0, 0)):
            browser.open(self.dossier, view='document_with_template')
            browser.fill({
                'form.widgets.template': str(getUtility(IIntIds).getId(self.asset_template)),
                'Title': 'Test Docx',
                }).save()

        document = self.dossier.listFolderContents()[-1]
        self.assertEquals(u'Test Docx.docx', document.file.filename)

        with TemporaryDocFile(document.file) as tmpfile:
            self.assertItemsEqual([], read_properties(tmpfile.path))

    @browsing
    def test_templates_without_a_file_are_not_listed(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='document_with_template')

        expected_documents = [
            u'T\xc3\xb6mpl\xc3\xb6te Mit',
            u'T\xc3\xb6mpl\xc3\xb6te Normal',
            u'T\xc3\xb6mpl\xc3\xb6te Ohne',
            u'T\xc3\xb6mpl\xc3\xb6te Sub',
            ]

        found_documents = [
            row.get('Title')
            for row in browser.css('table.listing').first.dicts()
            ]

        self.assertEquals(expected_documents, found_documents)
        self.assertNotIn(u'T\xc3\xb6mpl\xc3\xb6te Leer', found_documents)


class TestDocumentWithTemplateFormWithDocProperties(IntegrationTestCase):
    features = (
        'doc-properties',
        )

    def assert_doc_properties_updated_journal_entry_generated(self, document, user):
        entry = get_journal_entry(document)

        self.assertEqual(DOC_PROPERTIES_UPDATED, entry['action']['type'])
        self.assertEqual(user.id, entry['actor'])
        self.assertEqual('', entry['comments'])

    @browsing
    def test_properties_are_added_when_created_from_template_with_doc_properties(self, browser):
        self.login(self.regular_user, browser)

        with freeze(datetime(2020, 9, 28, 0, 0)):
            browser.open(self.dossier, view='document_with_template')
            browser.fill({
                'form.widgets.template': str(getUtility(IIntIds).getId(self.docprops_template)),
                'Title': 'Test Docx',
                }).save()

        document = self.dossier.listFolderContents()[-1]
        self.assertEquals(u'Test Docx.docx', document.file.filename)

        expected_doc_properties = {
            'Document.ReferenceNumber': 'Client1 1.1 / 1 / 35',
            'Document.SequenceNumber': '35',
            'Dossier.ReferenceNumber': 'Client1 1.1 / 1',
            'Dossier.Title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            'User.FullName': u'B\xe4rfuss K\xe4thi',
            'User.ID': 'kathi.barfuss',
            'ogg.document.document_date': datetime(2020, 9, 28, 0, 0),
            'ogg.document.reference_number': 'Client1 1.1 / 1 / 35',
            'ogg.document.sequence_number': '35',
            'ogg.document.title': 'Test Docx',
            'ogg.document.version_number': 0,
            'ogg.dossier.reference_number': 'Client1 1.1 / 1',
            'ogg.dossier.sequence_number': '1',
            'ogg.dossier.title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            'ogg.user.address1': 'Kappelenweg 13',
            'ogg.user.address2': 'Postfach 1234',
            'ogg.user.city': 'Vorkappelen',
            'ogg.user.country': 'Schweiz',
            'ogg.user.department': 'Staatskanzlei',
            'ogg.user.department_abbr': 'SK',
            'ogg.user.description': 'nix',
            'ogg.user.directorate': 'Staatsarchiv',
            'ogg.user.directorate_abbr': 'Arch',
            'ogg.user.email': 'foo@example.com',
            'ogg.user.email2': 'bar@example.com',
            'ogg.user.firstname': u'K\xe4thi',
            'ogg.user.lastname': u'B\xe4rfuss',
            'ogg.user.phone_fax': '012 34 56 77',
            'ogg.user.phone_mobile': '012 34 56 76',
            'ogg.user.phone_office': '012 34 56 78',
            'ogg.user.salutation': 'Prof. Dr.',
            'ogg.user.title': u'B\xe4rfuss K\xe4thi',
            'ogg.user.url': 'http://www.example.com',
            'ogg.user.userid': 'kathi.barfuss',
            'ogg.user.zip_code': '1234',
            }

        with TemporaryDocFile(document.file) as tmpfile:
            self.assertItemsEqual(
                expected_doc_properties.items() + [('Test', 'Peter')],
                read_properties(tmpfile.path))
        self.assert_doc_properties_updated_journal_entry_generated(document, self.regular_user)

    @browsing
    def test_properties_are_added_when_created_from_template_without_doc_properties(self, browser):
        self.login(self.regular_user, browser)

        with freeze(datetime(2020, 10, 28, 0, 0)):
            browser.open(self.dossier, view='document_with_template')
            browser.fill({
                'form.widgets.template': str(getUtility(IIntIds).getId(self.asset_template)),
                'Title': 'Test Docx',
                }).save()

        document = self.dossier.listFolderContents()[-1]
        self.assertEquals(u'Test Docx.docx', document.file.filename)

        expected_doc_properties = {
            'Document.ReferenceNumber': 'Client1 1.1 / 1 / 35',
            'Document.SequenceNumber': '35',
            'Dossier.ReferenceNumber': 'Client1 1.1 / 1',
            'Dossier.Title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            'User.FullName': u'B\xe4rfuss K\xe4thi',
            'User.ID': 'kathi.barfuss',
            'ogg.document.document_date': datetime(2020, 10, 28, 0, 0),
            'ogg.document.reference_number': 'Client1 1.1 / 1 / 35',
            'ogg.document.sequence_number': '35',
            'ogg.document.title': 'Test Docx',
            'ogg.document.version_number': 0,
            'ogg.dossier.reference_number': 'Client1 1.1 / 1',
            'ogg.dossier.sequence_number': '1',
            'ogg.dossier.title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            'ogg.user.address1': 'Kappelenweg 13',
            'ogg.user.address2': 'Postfach 1234',
            'ogg.user.city': 'Vorkappelen',
            'ogg.user.country': 'Schweiz',
            'ogg.user.department': 'Staatskanzlei',
            'ogg.user.department_abbr': 'SK',
            'ogg.user.description': 'nix',
            'ogg.user.directorate': 'Staatsarchiv',
            'ogg.user.directorate_abbr': 'Arch',
            'ogg.user.email': 'foo@example.com',
            'ogg.user.email2': 'bar@example.com',
            'ogg.user.firstname': u'K\xe4thi',
            'ogg.user.lastname': u'B\xe4rfuss',
            'ogg.user.phone_fax': '012 34 56 77',
            'ogg.user.phone_mobile': '012 34 56 76',
            'ogg.user.phone_office': '012 34 56 78',
            'ogg.user.salutation': 'Prof. Dr.',
            'ogg.user.title': u'B\xe4rfuss K\xe4thi',
            'ogg.user.url': 'http://www.example.com',
            'ogg.user.userid': 'kathi.barfuss',
            'ogg.user.zip_code': '1234',
            }

        with TemporaryDocFile(document.file) as tmpfile:
            self.assertItemsEqual(
                expected_doc_properties.items(),
                read_properties(tmpfile.path))
        self.assert_doc_properties_updated_journal_entry_generated(document, self.regular_user)


class TestDocumentWithTemplateFormWithContacts(FunctionalTestCase):
    document_date = datetime(2015, 9, 28, 0, 0)

    expected_doc_properties = {
        'Document.ReferenceNumber': 'Client1 / 1 / 2',
        'Document.SequenceNumber': '2',
        'Dossier.ReferenceNumber': 'Client1 / 1',
        'Dossier.Title': 'My Dossier',
        'User.FullName': 'Test User',
        'User.ID': TEST_USER_ID,
        'ogg.document.document_date': document_date,
        'ogg.document.reference_number': 'Client1 / 1 / 2',
        'ogg.document.sequence_number': '2',
        'ogg.document.title': 'Test Docx',
        'ogg.document.version_number': 0,
        'ogg.dossier.reference_number': 'Client1 / 1',
        'ogg.dossier.sequence_number': '1',
        'ogg.dossier.title': 'My Dossier',
        'ogg.user.email': 'test@example.org',
        'ogg.user.firstname': 'User',
        'ogg.user.lastname': 'Test',
        'ogg.user.title': 'Test User',
        'ogg.user.userid': TEST_USER_ID,
        }

    def setUp(self):
        super(TestDocumentWithTemplateFormWithContacts, self).setUp()
        api.portal.set_registry_record('create_doc_properties', True, interface=ITemplateFolderProperties)
        api.portal.set_registry_record('is_feature_enabled', True, interface=IContactSettings)

        self.setup_fullname(fullname='Peter')
        self.modification_date = datetime(2012, 12, 28)
        self.templatefolder = create(Builder('templatefolder'))

        self.template_word = create(
            Builder('document')
            .titled('Word Docx template')
            .within(self.templatefolder)
            .with_asset_file('without_custom_properties.docx'),
            )

        self.dossier = create(Builder('dossier').titled(u'My Dossier'))
        self.peter = create(Builder('person').having(firstname=u'Peter', lastname=u'M\xfcller'))

    def assert_doc_properties_updated_journal_entry_generated(self, document):
        entry = get_journal_entry(document)

        self.assertEqual(DOC_PROPERTIES_UPDATED, entry['action']['type'])
        self.assertEqual(TEST_USER_ID, entry['actor'])
        self.assertEqual('', entry['comments'])

    @staticmethod
    def _make_token(document):
        intids = getUtility(IIntIds)
        return str(intids.getId(document))

    @browsing
    def test_contact_recipient_properties_are_added(self, browser):
        address1 = create(
            Builder('address')
            .for_contact(self.peter)
            .labeled(u'Home')
            .having(
                street=u'Musterstrasse 283',
                zip_code=u'1234',
                city=u'Hinterkappelen',
                country=u'Schweiz',
                ),
            )

        create(
            Builder('address')
            .for_contact(self.peter)
            .labeled(u'Home')
            .having(
                street=u'Hauptstrasse 1',
                city=u'Vorkappelen',
                ),
            )

        mailaddress = create(
            Builder('mailaddress')
            .for_contact(self.peter)
            .having(address=u'foo@example.com'),
            )

        phonenumber = create(
            Builder('phonenumber')
            .for_contact(self.peter)
            .having(phone_number=u'1234 123 123'),
            )

        url = create(
            Builder('url')
            .for_contact(self.peter)
            .having(url=u'http://www.example.com'),
            )

        with freeze(self.document_date):
            # submit first wizard step
            browser.login().open(self.dossier, view='document_with_template')
            browser.fill({
                'form.widgets.template': self._make_token(self.template_word),
                'Title': 'Test Docx',
                })
            form = browser.find_form_by_field('Recipient')
            form.find_widget('Recipient').fill(get_contacts_token(self.peter))
            form.save()
            # submit second wizard step
            browser.fill({
                'form.widgets.address': str(address1.address_id),
                'form.widgets.mail_address': str(mailaddress.mailaddress_id),
                'form.widgets.phonenumber': str(phonenumber.phone_number_id),
                'form.widgets.url': str(url.url_id),
                }).save()

        document = self.dossier.listFolderContents()[0]
        self.assertEquals(u'Test Docx.docx', document.file.filename)

        expected_person_properties = {
            'ogg.recipient.contact.title': u'M\xfcller Peter',
            'ogg.recipient.person.firstname': 'Peter',
            'ogg.recipient.person.lastname': u'M\xfcller',
            'ogg.recipient.address.street': u'Musterstrasse 283',
            'ogg.recipient.address.zip_code': '1234',
            'ogg.recipient.address.city': 'Hinterkappelen',
            'ogg.recipient.address.country': 'Schweiz',
            'ogg.recipient.email.address': u'foo@example.com',
            'ogg.recipient.phone.number': u'1234 123 123',
            'ogg.recipient.url.url': u'http://www.example.com',
            }
        expected_person_properties.update(self.expected_doc_properties)

        with TemporaryDocFile(document.file) as tmpfile:
            self.assertItemsEqual(expected_person_properties.items(), read_properties(tmpfile.path))
        self.assert_doc_properties_updated_journal_entry_generated(document)

    @browsing
    def test_org_role_recipient_properties_are_added(self, browser):
        organization = create(
            Builder('organization')
            .having(name=u'Meier AG'),
            )

        org_role = create(
            Builder('org_role')
            .having(
                person=self.peter,
                organization=organization,
                function=u'cheffe',
                ),
            )

        create(
            Builder('address')
            .for_contact(organization)
            .labeled(u'Home')
            .having(
                street=u'Musterstrasse 283',
                zip_code=u'1234',
                city=u'Hinterkappelen',
                country=u'Schweiz',
                ),
            )

        mailaddress = create(
            Builder('mailaddress')
            .for_contact(organization)
            .having(address=u'foo@example.com'),
            )

        phonenumber = create(
            Builder('phonenumber')
            .for_contact(self.peter)
            .having(phone_number=u'1234 123 123'),
            )

        url = create(
            Builder('url')
            .for_contact(organization)
            .having(url=u'http://www.example.com'),
            )

        address_id = org_role.addresses[0].address_id

        with freeze(self.document_date):
            # submit first wizard step
            browser.login().open(self.dossier, view='document_with_template')
            browser.fill({
                'form.widgets.template': self._make_token(self.template_word),
                'Title': 'Test Docx',
                })
            form = browser.find_form_by_field('Recipient')
            form.find_widget('Recipient').fill(get_contacts_token(org_role))
            form.save()
            # submit second wizard step
            browser.fill({
                'form.widgets.address': address_id,
                'form.widgets.mail_address': str(mailaddress.mailaddress_id),
                'form.widgets.phonenumber': str(phonenumber.phone_number_id),
                'form.widgets.url': str(url.url_id),
                }).save()

        document = self.dossier.listFolderContents()[0]
        self.assertEquals(u'Test Docx.docx', document.file.filename)
        expected_org_role_properties = {
            'ogg.recipient.contact.title': u'M\xfcller Peter',
            'ogg.recipient.person.firstname': 'Peter',
            'ogg.recipient.person.lastname': u'M\xfcller',
            'ogg.recipient.orgrole.function': u'cheffe',
            'ogg.recipient.organization.name': u'Meier AG',
            'ogg.recipient.address.street': u'Musterstrasse 283',
            'ogg.recipient.address.zip_code': '1234',
            'ogg.recipient.address.city': 'Hinterkappelen',
            'ogg.recipient.address.country': 'Schweiz',
            'ogg.recipient.email.address': u'foo@example.com',
            'ogg.recipient.phone.number': u'1234 123 123',
            'ogg.recipient.url.url': u'http://www.example.com',
            }
        expected_org_role_properties.update(self.expected_doc_properties)

        with TemporaryDocFile(document.file) as tmpfile:
            self.assertItemsEqual(expected_org_role_properties.items(), read_properties(tmpfile.path))
        self.assert_doc_properties_updated_journal_entry_generated(document)

    @browsing
    def test_ogds_user_recipient_properties_are_added(self, browser):
        ogds_user = create(
            Builder('ogds_user')
            .id('ogds-peter')
            .having(**OGDS_USER_ATTRIBUTES)
            .as_contact_adapter(),
            )

        with freeze(self.document_date):
            # submit first wizard step
            browser.login().open(self.dossier, view='document_with_template')
            browser.fill({
                'form.widgets.template': self._make_token(self.template_word),
                'Title': 'Test Docx',
                })
            form = browser.find_form_by_field('Recipient')
            form.find_widget('Recipient').fill(get_contacts_token(ogds_user))
            form.save()
            # submit second wizard step
            browser.fill({
                'form.widgets.address': '{}_1'.format(ogds_user.id),
                'form.widgets.mail_address': '{}_2'.format(ogds_user.id),
                'form.widgets.phonenumber': '{}_3'.format(ogds_user.id),
                'form.widgets.url': '{}_1'.format(ogds_user.id),
                }).save()

        document = self.dossier.listFolderContents()[0]
        self.assertEquals(u'Test Docx.docx', document.file.filename)

        expected_org_role_properties = {
            'ogg.recipient.contact.title': u'M\xfcller Peter',
            'ogg.recipient.contact.description': u'nix',
            'ogg.recipient.person.salutation': 'Prof. Dr.',
            'ogg.recipient.person.firstname': 'Peter',
            'ogg.recipient.person.lastname': u'M\xfcller',
            'ogg.recipient.address.street': u'Kappelenweg 13, Postfach 1234',
            'ogg.recipient.address.zip_code': '1234',
            'ogg.recipient.address.city': u'Vorkappelen',
            'ogg.recipient.address.country': u'Schweiz',
            'ogg.recipient.email.address': u'bar@example.com',
            'ogg.recipient.phone.number': u'012 34 56 76',
            'ogg.recipient.url.url': u'http://www.example.com',
        }
        expected_org_role_properties.update(self.expected_doc_properties)

        with TemporaryDocFile(document.file) as tmpfile:
            self.assertItemsEqual(expected_org_role_properties.items(), read_properties(tmpfile.path))
        self.assert_doc_properties_updated_journal_entry_generated(document)


class TestDocumentWithTemplateFormWithOfficeConnector(IntegrationTestCase):
    features = (
        'officeconnector-checkout',
        )

    @browsing
    def test_opens_doc_with_officeconnector_when_feature_flaged(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='document_with_template')
        browser.fill({
            'form.widgets.template': str(getUtility(IIntIds).getId(self.normal_template)),
            'Title': 'Test OfficeConnector',
            }).save()

        self.assertIn(
            "'oc:",
            browser.css('script.redirector').first.text,
            'OfficeConnector redirection script not found',
            )


class TestTemplateFolder(FunctionalTestCase):

    @browsing
    def test_adding(self, browser):
        self.grant('Manager')
        add_languages(['de-ch'])
        browser.login().open(self.portal)
        factoriesmenu.add('Template Folder')

        browser.fill({'Title': 'Templates'}).save()

        self.assertTrue(ITemplateFolder.providedBy(browser.context))

    @browsing
    def test_is_only_addable_by_manager(self, browser):
        browser.login().open(self.portal)

        self.grant('Administrator')
        browser.reload()
        self.assertNotIn(
            'Template Folder',
            factoriesmenu.addable_types()
            )

        self.grant('Manager')
        browser.reload()
        self.assertIn(
            'Template Folder',
            factoriesmenu.addable_types()
            )

    @browsing
    def test_manager_addable_types(self, browser):
        self.grant('Manager')
        templatefolder = create(Builder('templatefolder'))
        browser.login().open(templatefolder)

        self.assertEquals(
            ['Document', 'TaskTemplateFolder', 'Template Folder'],
            factoriesmenu.addable_types())

    @skip("This test currently fails in a flaky way on CI."
          "See https://github.com/4teamwork/opengever.core/issues/3995")
    @browsing
    def test_supports_translated_title(self, browser):
        add_languages(['de-ch', 'fr-ch'])
        self.grant('Manager')
        browser.login().open()
        factoriesmenu.add('Template Folder')
        browser.fill({'Title (German)': u'Vorlagen',
                      'Title (French)': u'mod\xe8le'})
        browser.find('Save').click()

        browser.find(u'Français').click()
        self.assertEquals(u'mod\xe8le', browser.css('h1').first.text)

        browser.find('Deutsch').click()
        self.assertEquals(u'Vorlagen', browser.css('h1').first.text)

    @browsing
    def test_do_not_show_dossier_templates_tab(self, browser):
        templatefolder = create(Builder('templatefolder'))

        browser.login().visit(templatefolder)

        self.assertEqual(0, len(browser.css('.formTab #tab-dossiertemplates')))

    @browsing
    def test_portlet_inheritance_is_blocked(self, browser):
        self.grant('Manager')
        add_languages(['de-ch'])
        browser.login().open(self.portal)
        factoriesmenu.add('Template Folder')
        browser.fill({'Title': 'Templates'}).save()

        self.assert_portlet_inheritance_blocked(
            'plone.leftcolumn', browser.context)

    @browsing
    def test_navigation_portlet_is_added(self, browser):
        self.grant('Manager')
        add_languages(['de-ch'])
        browser.login().open(self.portal)
        factoriesmenu.add('Template Folder')
        browser.fill({'Title': 'Templates'}).save()

        manager = getUtility(
            IPortletManager, name=u'plone.leftcolumn', context=browser.context)
        mapping = getMultiAdapter(
            (browser.context, manager), IPortletAssignmentMapping)

        portlet = mapping.get('navigation')

        self.assertIsNotNone(
            portlet, 'Navigation portlet not added to Templatefolder')
        self.assertEqual(0, portlet.topLevel)
        self.assertEquals('opengever-dossier-templatefolder', portlet.root)

    @browsing
    def test_portlets_are_inherited_on_sub_templatefolder(self, browser):
        templatefolder = create(Builder('templatefolder'))
        self.grant('Manager')
        add_languages(['de-ch'])
        browser.login().open(templatefolder)
        factoriesmenu.add('Template Folder')
        browser.fill({'Title': 'Templates'}).save()

        manager = getUtility(
            IPortletManager, name=u'plone.leftcolumn', context=browser.context)
        assignable = getMultiAdapter(
            (browser.context, manager), ILocalPortletAssignmentManager)
        self.assertFalse(assignable.getBlacklistStatus(CONTEXT_CATEGORY))


class TestTemplateFolderMeetingEnabled(IntegrationTestCase):

    features = (
        'meeting',
        )

    @browsing
    def test_addable_types_with_meeting_feature(self, browser):
        self.login(self.manager, browser)
        browser.open(self.templates)

        expected_addable_types = [
            'Document',
            'Meeting Template',
            'Proposal Template',
            'Sablon Template',
            'TaskTemplateFolder',
            'Template Folder',
            ]

        addable_types = factoriesmenu.addable_types()

        self.assertItemsEqual(expected_addable_types, addable_types)


class TestTemplateFolderUtility(FunctionalTestCase):

    def test_get_template_folder_returns_path_of_the_templatefolder(self):
        templatefolder = create(Builder('templatefolder'))

        self.assertEquals(templatefolder, get_template_folder())

    def test_get_template_folder_returns_allways_root_templatefolder(self):
        templatefolder = create(Builder('templatefolder'))
        create(Builder('templatefolder')
               .within(templatefolder))

        self.assertEquals(templatefolder, get_template_folder())


class TestTemplateFolderListings(IntegrationTestCase):

    @browsing
    def test_renders_quickupload_uploadbox(self, browser):
        self.login(self.administrator, browser)  # admins can add templates
        browser.open(self.templates)

        self.assertIsNotNone(
            browser.css('#uploadbox').first,
            'Upload box should be available in template folders')

    @browsing
    def test_receipt_delivery_and_subdossier_column_are_hidden_in_document_tab(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.templates, view='tabbedview_view-documents')

        expected_table_header = [
            '',
            'Sequence Number',
            'Title',
            'Document Author',
            'Document Date',
            'Checked out by',
            'Public Trial',
            'Reference Number',
            ]

        self.assertEquals(expected_table_header, browser.css('table.listing').first.lists()[0])

    @browsing
    def test_receipt_delivery_and_subdossier_column_are_hidden_in_sablon_template_tab(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.templates, view='tabbedview_view-sablontemplates')

        expected_table_header = [
            '',
            'Sequence Number',
            'Title',
            'Document Author',
            'Document Date',
            'Checked out by',
            'Public Trial',
            'Reference Number',
            ]

        self.assertEquals(expected_table_header, browser.css('table.listing').first.lists()[0])

    @browsing
    def test_receipt_delivery_and_subdossier_column_are_hidden_in_proposal_templates_tab(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.templates, view='tabbedview_view-proposaltemplates')

        expected_table_header = [
            '',
            'Sequence Number',
            'Title',
            'Document Author',
            'Document Date',
            'Checked out by',
            'Public Trial',
            'Reference Number',
            ]

        self.assertEquals(expected_table_header, browser.css('table.listing').first.lists()[0])

    @browsing
    def test_enabled_actions_are_limited_in_document_tab(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.templates, view='tabbedview_view-documents')

        expected_action_menu_content = [
            'Export as Zip',
            'Copy Items',
            'Export selection',
            'Move Items',
            ]

        self.assertItemsEqual(expected_action_menu_content, browser.css('.actionMenuContent li').text)

        self.login(self.administrator, browser)
        browser.open(self.templates, view='tabbedview_view-documents')

        expected_action_menu_content = [
            'Export as Zip',
            'Copy Items',
            'Checkin with comment',
            'Checkin without comment',
            'Export selection',
            'Delete',
            'Move Items',
            ]

        self.assertItemsEqual(expected_action_menu_content, browser.css('.actionMenuContent li').text)

        self.login(self.manager, browser)
        browser.open(self.templates, view='tabbedview_view-documents')

        self.assertItemsEqual(expected_action_menu_content, browser.css('.actionMenuContent li').text)

    @browsing
    def test_document_tab_lists_only_documents_directly_beneath(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.templates, view='tabbedview_view-documents')

        templates = browser.css('table.listing').first.dicts(as_text=False)
        self.assertEqual(4, len(templates))

        expected_document_urls = [
            self.docprops_template.absolute_url(),
            self.asset_template.absolute_url(),
            self.normal_template.absolute_url(),
            self.empty_template.absolute_url(),
            ]

        document_urls = [
            element.get('Title').css('a').first.get('href')
            for element in templates
            ]

        self.assertEqual(expected_document_urls, document_urls)
        self.assertNotIn(self.subtemplate.absolute_url(), document_urls)

    @browsing
    def test_enabled_actions_are_limited_in_sablontemplates_tab(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.templates, view='tabbedview_view-sablontemplates')

        expected_actions = [
            'Export as Zip',
            'Copy Items',
            'Export selection',
            ]

        self.assertItemsEqual(expected_actions, browser.css('.actionMenuContent li').text)

        self.login(self.administrator, browser)
        browser.open(self.templates, view='tabbedview_view-sablontemplates')

        expected_actions = [
            'Export as Zip',
            'Copy Items',
            'Checkin with comment',
            'Checkin without comment',
            'Export selection',
            'Delete',
            ]

        self.assertItemsEqual(expected_actions, browser.css('.actionMenuContent li').text)

        self.login(self.manager, browser)
        browser.open(self.templates, view='tabbedview_view-sablontemplates')

        self.assertItemsEqual(expected_actions, browser.css('.actionMenuContent li').text)

    @browsing
    def test_enabled_actions_are_limited_in_proposaltemplates_tab(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.templates, view='tabbedview_view-proposaltemplates')

        expected_actions = [
            'Export as Zip',
            'Copy Items',
            'Export selection',
            ]

        self.assertItemsEqual(expected_actions, browser.css('.actionMenuContent li').text)

        self.login(self.administrator, browser)
        browser.open(self.templates, view='tabbedview_view-proposaltemplates')

        expected_actions = [
            'Export as Zip',
            'Copy Items',
            'Checkin with comment',
            'Checkin without comment',
            'Export selection',
            'Delete',
            ]

        self.assertItemsEqual(expected_actions, browser.css('.actionMenuContent li').text)

        self.login(self.manager, browser)
        browser.open(self.templates, view='tabbedview_view-proposaltemplates')

        self.assertItemsEqual(expected_actions, browser.css('.actionMenuContent li').text)

    @browsing
    def test_sablontemplates_tab_lists_only_documents_directly_beneath(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.templates, view='tabbedview_view-sablontemplates')

        templates = browser.css('table.listing').first.dicts(as_text=False)
        self.assertEqual(1, len(templates))

        document_link = templates[0]['Title'].css('a').first.get('href')
        self.assertEqual(self.sablon_template.absolute_url(), document_link)

    @browsing
    def test_proposaltemplates_tab_lists_only_documents_directly_beneath(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.templates, view='tabbedview_view-proposaltemplates')

        templates = browser.css('table.listing').first.dicts(as_text=False)
        self.assertEqual(3, len(templates))

        document_link = templates[0]['Title'].css('a').first.get('href')
        self.assertEqual(self.proposal_template.absolute_url(), document_link)


class TestTemplateDocumentTabs(IntegrationTestCase):

    features = ('bumblebee', )

    @browsing
    def test_template_overview_tab(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.normal_template, view='tabbedview_view-overview')

        self.assertIn(['Title', u'T\xc3\xb6mpl\xc3\xb6te Normal'], browser.css('table.listing').first.lists())

    @browsing
    def test_template_journal_tab(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.normal_template, view='tabbedview_view-journal')

        journal_entries = browser.css('table.listing').first.dicts()

        self.assertEqual(Actor.lookup(self.administrator.id).get_label(), journal_entries[0]['Changed by'])
        self.assertEqual(u'Document added: T\xc3\xb6mpl\xc3\xb6te Normal', journal_entries[0]['Title'])

    @browsing
    def test_documents_tab_shows_only_docs_directly_inside_the_folder(self, browser):
        self.login(self.regular_user, browser=browser)

        # main templatefolder
        browser.open(self.templates, view='tabbedview_view-documents-gallery')
        self.assertEquals(
            [self.empty_template.title, self.normal_template.title,
             self.asset_template.title, self.docprops_template.title],
            [img.attrib.get('alt') for img in browser.css('img')])

        # subtemplatefolder
        browser.open(self.subtemplates, view='tabbedview_view-documents-gallery')
        self.assertEquals(
            [self.subtemplate.title],
            [img.attrib.get('alt') for img in browser.css('img')])


class TestDossierTemplateFeature(IntegrationTestCase):
    features = (
        'dossiertemplate',
        )

    @browsing
    def test_dossier_template_is_addable_if_dossier_template_feature_is_enabled(self, browser):
        self.login(self.manager, browser)
        browser.open(self.templates)

        expected_addable_types = ['Document',
                                  'Dossier template',
                                  'TaskTemplateFolder',
                                  'Template Folder']
        self.assertEqual(expected_addable_types, factoriesmenu.addable_types())

    @browsing
    def test_show_dossier_templates_tab(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.templates)

        self.assertEqual('Dossier templates', browser.css('.formTab #tab-dossiertemplates').first.text)

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
from opengever.core.testing import activate_meeting_word_implementation
from opengever.core.testing import OPENGEVER_FUNCTIONAL_DOSSIER_TEMPLATE_LAYER
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.dossier.docprops import TemporaryDocFile
from opengever.dossier.interfaces import ITemplateFolderProperties
from opengever.dossier.templatefolder import get_template_folder
from opengever.dossier.templatefolder.interfaces import ITemplateFolder
from opengever.dossier.tests import OGDS_USER_ATTRIBUTES
from opengever.journal.handlers import DOC_PROPERTIES_UPDATED
from opengever.journal.tests.utils import get_journal_entry
from opengever.officeconnector.interfaces import IOfficeConnectorSettings
from opengever.ogds.base.actor import Actor
from opengever.testing import add_languages
from opengever.testing import FunctionalTestCase
from opengever.testing.helpers import get_contacts_token
from opengever.testing.pages import sharing_tab_data
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.registry.interfaces import IRegistry
from zope.app.intid.interfaces import IIntIds
from zope.component import getMultiAdapter
from zope.component import getUtility
import re
import transaction


def _make_token(document):
    intids = getUtility(IIntIds)
    return str(intids.getId(document))


class TestDocumentWithTemplateForm(FunctionalTestCase):

    document_date = datetime(2015, 9, 28, 0, 0)

    expected_doc_properties = {
         'Document.ReferenceNumber': 'Client1 / 2 / 4',
         'Document.SequenceNumber': '4',
         'Dossier.ReferenceNumber': 'Client1 / 2',
         'Dossier.Title': 'My Dossier',
         'User.FullName': 'Test User',
         'User.ID': TEST_USER_ID,
         'ogg.document.document_date': document_date,
         'ogg.document.reference_number': 'Client1 / 2 / 4',
         'ogg.document.sequence_number': '4',
         'ogg.document.title': 'Test Docx',
         'ogg.dossier.reference_number': 'Client1 / 2',
         'ogg.dossier.sequence_number': '2',
         'ogg.dossier.title': 'My Dossier',
         'ogg.user.email': 'test@example.org',
         'ogg.user.firstname': 'User',
         'ogg.user.lastname': 'Test',
         'ogg.user.title': 'Test User',
         'ogg.user.userid': TEST_USER_ID
    }

    def setUp(self):
        super(TestDocumentWithTemplateForm, self).setUp()
        self.setup_fullname(fullname='Peter')

        registry = getUtility(IRegistry)
        self.props = registry.forInterface(ITemplateFolderProperties)
        self.props.create_doc_properties = True

        self.modification_date = datetime(2012, 12, 28)

        self.templatefolder = create(Builder('templatefolder'))
        self.template_a = create(Builder('document')
                                 .titled('Template A')
                                 .with_dummy_content()
                                 .within(self.templatefolder)
                                 .with_dummy_content()
                                 .with_modification_date(self.modification_date))
        self.template_b = create(Builder('document')
                                 .titled('Template B')
                                 .within(self.templatefolder)
                                 .with_dummy_content()
                                 .with_modification_date(self.modification_date))
        self.dossier = create(Builder('dossier').titled(u'My Dossier'))

        self.template_b_token = _make_token(self.template_b)

    def assert_doc_properties_updated_journal_entry_generated(self, document):
        entry = get_journal_entry(document)

        self.assertEqual(DOC_PROPERTIES_UPDATED, entry['action']['type'])
        self.assertEqual(TEST_USER_ID, entry['actor'])
        self.assertEqual('', entry['comments'])

    @browsing
    def test_templates_are_sorted_alphabetically_ascending(self, browser):
        create(Builder('document')
               .titled('AAA Template')
               .within(self.templatefolder)
               .with_dummy_content()
               .with_modification_date(datetime(2010, 12, 28)))

        browser.login().open(self.dossier, view='document_with_template')
        self.assertEquals(
            [{'': '',
              'Creator': 'test_user_1_',
              'Modified': '28.12.2010',
              'Title': 'AAA Template'},

             {'': '',
              'Creator': 'test_user_1_',
              'Modified': '28.12.2012',
              'Title': 'Template A'},

             {'': '',
              'Creator': 'test_user_1_',
              'Modified': '28.12.2012',
              'Title': 'Template B'}],
            browser.css('table.listing').first.dicts())

    @browsing
    def test_form_list_all_templates(self, browser):
        browser.login().open(self.dossier, view='document_with_template')
        self.assertEquals(
            [{'': '',
              'Creator': 'test_user_1_',
              'Modified': '28.12.2012',
              'Title': 'Template A'},

             {'': '',
              'Creator': 'test_user_1_',
              'Modified': '28.12.2012',
              'Title': 'Template B'}],
            browser.css('table.listing').first.dicts())

    @browsing
    def test_template_list_includes_nested_templates(self, browser):
        subtemplatefolder = create(Builder('templatefolder')
                                    .within(self.templatefolder))
        create(Builder('document')
               .titled('Template C')
               .within(subtemplatefolder)
               .with_dummy_content()
               .with_modification_date(self.modification_date))

        browser.login().open(self.dossier, view='document_with_template')

        self.assertEquals(
            [{'': '',
              'Creator': 'test_user_1_',
              'Modified': '28.12.2012',
              'Title': 'Template A'},
             {'': '',
              'Creator': 'test_user_1_',
              'Modified': '28.12.2012',
              'Title': 'Template B'},
             {'': '',
              'Creator': 'test_user_1_',
              'Modified': '28.12.2012',
              'Title': 'Template C'}],

            browser.css('table.listing').first.dicts())

    @browsing
    def test_form_does_not_inlcude_participants_with_disabled_feature(self, browser):
        browser.login().open(self.dossier, view='document_with_template')

        # The CheckBoxWidget is rendered with two labels (only in testing).
        # The reason for that is a wrong widget renderer adapter lookup because
        # of the stacked globalregistry (see plone.testing.zca: pushGlobalRegistry
        # for more information).
        self.assertEqual([u'Template', u'Title', u'', u'Edit after creation'],
                         browser.css('#form label').text)

    @browsing
    def test_cancel_redirects_to_the_dossier(self, browser):
        browser.login().open(self.dossier, view='document_with_template')
        browser.find('Cancel').click()
        self.assertEquals(self.dossier, browser.context)
        self.assertEquals('tabbed_view', plone.view())

    @browsing
    def test_save_redirects_to_the_dossiers_document_tab(self, browser):
        browser.login().open(self.dossier, view='document_with_template')
        browser.fill({'form.widgets.template': self.template_b_token,
                      'Title': 'Test Document',
                      'Edit after creation': False}).save()

        self.assertEquals(self.dossier, browser.context)
        self.assertEquals(self.dossier.absolute_url() + '#documents',
                          browser.url)

    @browsing
    def test_new_document_is_titled_with_the_form_value(self, browser):
        browser.login().open(self.dossier, view='document_with_template')
        browser.fill({'form.widgets.template': self.template_b_token,
                      'Title': 'Test Document'}).save()

        document = self.dossier.listFolderContents()[0]

        self.assertEquals('Test Document', document.title)

    @browsing
    def test_new_document_values_are_filled_with_default_values(self, browser):
        browser.login().open(self.dossier, view='document_with_template')
        browser.fill({'form.widgets.template': self.template_b_token,
                      'Title': 'Test Document'}).save()

        document = self.dossier.listFolderContents()[0]
        self.assertEquals(date.today(), document.document_date)
        self.assertEquals(u'privacy_layer_no', document.privacy_layer)

    @browsing
    def test_file_of_the_new_document_is_a_copy_of_the_template(self, browser):
        browser.login().open(self.dossier, view='document_with_template')
        browser.fill({'form.widgets.template': self.template_b_token,
                      'Title': 'Test Document'}).save()

        document = self.dossier.listFolderContents()[0]

        self.assertEquals(self.template_b.file.data, document.file.data)
        self.assertNotEquals(self.template_b.file, document.file)

    @browsing
    def test_contact_recipient_properties_are_added(self, browser):
        api.portal.set_registry_record(
            'is_feature_enabled', True, interface=IContactSettings)

        template_word = create(Builder('document')
                               .titled('Word Docx template')
                               .within(self.templatefolder)
                               .with_asset_file('without_custom_properties.docx'))
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))
        address1 = create(Builder('address')
                          .for_contact(peter)
                          .labeled(u'Home')
                          .having(street=u'Musterstrasse 283',
                                  zip_code=u'1234',
                                  city=u'Hinterkappelen',
                                  country=u'Schweiz'))
        address2 = create(Builder('address')
                          .for_contact(peter)
                          .labeled(u'Home')
                          .having(street=u'Hauptstrasse 1',
                                  city=u'Vorkappelen'))
        mailaddress = create(Builder('mailaddress')
                             .for_contact(peter)
                             .having(address=u'foo@example.com'))
        phonenumber = create(Builder('phonenumber')
                             .for_contact(peter)
                             .having(phone_number=u'1234 123 123'))
        url = create(Builder('url')
                     .for_contact(peter)
                     .having(url=u'http://www.example.com'))

        with freeze(self.document_date):
            # submit first wizard step
            browser.login().open(self.dossier, view='document_with_template')
            browser.fill({'form.widgets.template': _make_token(template_word),
                          'Title': 'Test Docx'})
            form = browser.find_form_by_field('Recipient')
            form.find_widget('Recipient').fill(get_contacts_token(peter))
            form.save()
            # submit second wizard step
            browser.fill(
                {'form.widgets.address': str(address1.address_id),
                 'form.widgets.mail_address': str(mailaddress.mailaddress_id),
                 'form.widgets.phonenumber': str(phonenumber.phone_number_id),
                 'form.widgets.url': str(url.url_id)}
            ).save()

        document = self.dossier.listFolderContents()[0]
        self.assertEquals(u'test-docx.docx', document.file.filename)

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
            self.assertItemsEqual(
                expected_person_properties.items(),
                read_properties(tmpfile.path))
        self.assert_doc_properties_updated_journal_entry_generated(document)

    @browsing
    def test_org_role_recipient_properties_are_added(self, browser):
        api.portal.set_registry_record(
            'is_feature_enabled', True, interface=IContactSettings)

        template_word = create(Builder('document')
                               .titled('Word Docx template')
                               .within(self.templatefolder)
                               .with_asset_file('without_custom_properties.docx'))
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))
        organization = create(Builder('organization')
                              .having(name=u'Meier AG'))
        org_role = create(Builder('org_role').having(
            person=peter, organization=organization, function=u'cheffe'))

        address1 = create(Builder('address')
                          .for_contact(organization)
                          .labeled(u'Home')
                          .having(street=u'Musterstrasse 283',
                                  zip_code=u'1234',
                                  city=u'Hinterkappelen',
                                  country=u'Schweiz'))
        mailaddress = create(Builder('mailaddress')
                             .for_contact(organization)
                             .having(address=u'foo@example.com'))
        phonenumber = create(Builder('phonenumber')
                             .for_contact(peter)
                             .having(phone_number=u'1234 123 123'))
        url = create(Builder('url')
                     .for_contact(organization)
                     .having(url=u'http://www.example.com'))
        address_id = org_role.addresses[0].address_id

        with freeze(self.document_date):
            # submit first wizard step
            browser.login().open(self.dossier, view='document_with_template')
            browser.fill({'form.widgets.template': _make_token(template_word),
                          'Title': 'Test Docx'})
            form = browser.find_form_by_field('Recipient')
            form.find_widget('Recipient').fill(get_contacts_token(org_role))
            form.save()
            # submit second wizard step
            browser.fill(
                {'form.widgets.address': address_id,
                 'form.widgets.mail_address': str(mailaddress.mailaddress_id),
                 'form.widgets.phonenumber': str(phonenumber.phone_number_id),
                 'form.widgets.url': str(url.url_id)}
            ).save()

        document = self.dossier.listFolderContents()[0]
        self.assertEquals(u'test-docx.docx', document.file.filename)
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
            self.assertItemsEqual(
                expected_org_role_properties.items(),
                read_properties(tmpfile.path))
        self.assert_doc_properties_updated_journal_entry_generated(document)

    @browsing
    def test_ogds_user_recipient_properties_are_added(self, browser):
        api.portal.set_registry_record(
            'is_feature_enabled', True, interface=IContactSettings)

        template_word = create(Builder('document')
                               .titled('Word Docx template')
                               .within(self.templatefolder)
                               .with_asset_file('without_custom_properties.docx'))

        ogds_user = create(Builder('ogds_user')
                           .id('peter')
                           .having(**OGDS_USER_ATTRIBUTES)
                           .as_contact_adapter())

        with freeze(self.document_date):
            # submit first wizard step
            browser.login().open(self.dossier, view='document_with_template')
            browser.fill({'form.widgets.template': _make_token(template_word),
                          'Title': 'Test Docx'})
            form = browser.find_form_by_field('Recipient')
            form.find_widget('Recipient').fill(get_contacts_token(ogds_user))
            form.save()
            # submit second wizard step
            browser.fill(
                {'form.widgets.address': '{}_1'.format(ogds_user.id),
                 'form.widgets.mail_address': '{}_2'.format(ogds_user.id),
                 'form.widgets.phonenumber': '{}_3'.format(ogds_user.id),
                 'form.widgets.url': '{}_1'.format(ogds_user.id)}
            ).save()

        document = self.dossier.listFolderContents()[0]
        self.assertEquals(u'test-docx.docx', document.file.filename)

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
            self.assertItemsEqual(
                expected_org_role_properties.items(),
                read_properties(tmpfile.path))
        self.assert_doc_properties_updated_journal_entry_generated(document)

    @browsing
    def test_properties_are_added_when_created_from_template_with_doc_properties(self, browser):
        template_word = create(Builder('document')
                               .titled('Word Docx template')
                               .within(self.templatefolder)
                               .with_asset_file('with_custom_properties.docx'))

        with freeze(self.document_date):
            browser.login().open(self.dossier, view='document_with_template')
            browser.fill({'form.widgets.template': _make_token(template_word),
                          'Title': 'Test Docx'}).save()

        document = self.dossier.listFolderContents()[0]
        self.assertEquals(u'test-docx.docx', document.file.filename)
        with TemporaryDocFile(document.file) as tmpfile:
            self.assertItemsEqual(
                self.expected_doc_properties.items() + [('Test', 'Peter')],
                read_properties(tmpfile.path))
        self.assert_doc_properties_updated_journal_entry_generated(document)

    @browsing
    def test_properties_are_added_when_created_from_template_without_doc_properties(self, browser):
        template_word = create(Builder('document')
                               .titled('Word Docx template')
                               .within(self.templatefolder)
                               .with_asset_file('without_custom_properties.docx'))

        with freeze(self.document_date):
            browser.login().open(self.dossier, view='document_with_template')
            browser.fill({'form.widgets.template': _make_token(template_word),
                          'Title': 'Test Docx'}).save()

        document = self.dossier.listFolderContents()[0]
        self.assertEquals(u'test-docx.docx', document.file.filename)
        with TemporaryDocFile(document.file) as tmpfile:
            self.assertItemsEqual(
                self.expected_doc_properties.items(),
                read_properties(tmpfile.path))
        self.assert_doc_properties_updated_journal_entry_generated(document)

    @browsing
    def test_doc_properties_are_not_created_when_disabled(self, browser):
        self.props.create_doc_properties = False
        template_word = create(Builder('document')
                               .titled('Word Docx template')
                               .within(self.templatefolder)
                               .with_asset_file('without_custom_properties.docx'))

        browser.login().open(self.dossier, view='document_with_template')
        browser.fill({'form.widgets.template': _make_token(template_word),
                      'Title': 'Test Docx'}).save()

        document = self.dossier.listFolderContents()[0]
        self.assertEquals(u'test-docx.docx', document.file.filename)
        with TemporaryDocFile(document.file) as tmpfile:
            self.assertItemsEqual([], read_properties(tmpfile.path))

    @browsing
    def test_templates_without_a_file_are_not_listed(self, browser):
        create(Builder('document')
               .titled(u'Template with no content')
               .within(self.templatefolder))

        browser.login().open(self.dossier, view='document_with_template')

        self.assertEquals(
            ['Template A', 'Template B'],
            [row.get('Title')
             for row in browser.css('table.listing').first.dicts()])

    @browsing
    def test_opens_doc_with_officeconnector_when_feature_flaged(self, browser):
        api.portal.set_registry_record('direct_checkout_and_edit_enabled',
                                       True,
                                       interface=IOfficeConnectorSettings)

        template_word = create(Builder('document')
                               .titled('Word Docx template')
                               .within(self.templatefolder)
                               .with_dummy_content())

        browser.login().open(self.dossier, view='document_with_template')
        browser.fill({'form.widgets.template': _make_token(template_word),
                      'Title': 'Test OfficeConnector'}).save()

        self.assertIn(
            "'oc:",
            browser.css('script.redirector').first.text,
            'OfficeConnector redirection script not found')


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

    @browsing
    def test_supports_translated_title(self, browser):
        add_languages(['de-ch', 'fr-ch'])
        self.grant('Manager')
        browser.login().open()
        factoriesmenu.add('Template Folder')
        browser.fill({'Title (German)': u'Vorlagen',
                      'Title (French)': u'mod\xe8le'})
        browser.find('Save').click()

        browser.find('FR').click()
        self.assertEquals(u'mod\xe8le', browser.css('h1').first.text)

        browser.find('DE').click()
        self.assertEquals(u'Vorlagen', browser.css('h1').first.text)

    @browsing
    def test_do_not_show_dossier_templates_tab(self, browser):
        templatefolder = create(Builder('templatefolder'))

        browser.login().visit(templatefolder)

        self.assertEqual(0, len(browser.css('.formTab #tab-dossiertemplates')))

    @browsing
    def test_prefill_responsible_user(self, browser):
        self.grant('Manager')
        add_languages(['de-ch'])
        browser.login().open(self.portal)
        factoriesmenu.add('Template Folder')

        self.assertEqual(
            'Test User (test_user_1_)',
            browser.css('#formfield-form-widgets-IDossier-responsible option[selected]').first.text
            )

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


class TestTemplateFolderMeetingEnabled(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestTemplateFolderMeetingEnabled, self).setUp()
        self.grant('Manager')

    @browsing
    def test_addable_types_with_meeting_feature(self, browser):
        templatefolder = create(Builder('templatefolder'))
        browser.login().open(templatefolder)

        self.assertEquals(
            ['Document', 'Sablon Template', 'TaskTemplateFolder',
             'Template Folder'],
            factoriesmenu.addable_types())

    @browsing
    def test_addable_types_with_meeting_word_implementation(self, browser):
        activate_meeting_word_implementation()
        templatefolder = create(Builder('templatefolder'))
        browser.login().open(templatefolder)

        self.assertEquals(
            ['Document', 'Proposal Template', 'Sablon Template',
             'TaskTemplateFolder', 'Template Folder'],
            factoriesmenu.addable_types())


class TestTemplateFolderUtility(FunctionalTestCase):

    def test_get_template_folder_returns_path_of_the_templatefolder(self):
        templatefolder = create(Builder('templatefolder'))

        self.assertEquals(templatefolder, get_template_folder())

    def test_get_template_folder_returns_allways_root_templatefolder(self):
        templatefolder = create(Builder('templatefolder'))
        create(Builder('templatefolder')
               .within(templatefolder))

        self.assertEquals(templatefolder, get_template_folder())


OVERVIEW_TAB = 'tabbedview_view-overview'
DOCUMENT_TAB = 'tabbedview_view-documents'
TRASH_TAB = 'tabbedview_view-trash'
JOURNAL_TAB = 'tabbedview_view-journal'
INFO_TAB = 'tabbedview_view-sharing'
SABLONTEMPLATES_TAB = 'tabbedview_view-sablontemplates'
PROPOSALTEMPLATES_TAB = 'tabbedview_view-proposaltemplates'


class TestTemplateFolderListings(FunctionalTestCase):

    def setUp(self):
        super(TestTemplateFolderListings, self).setUp()

        self.templatefolder = create(Builder('templatefolder'))
        self.dossier = create(Builder('dossier'))
        self.template = create(Builder('sablontemplate')
                               .within(self.templatefolder))
        self.proposaltemplate = create(Builder('proposaltemplate')
                                       .within(self.templatefolder))
        self.document = create(Builder('document')
                               .within(self.templatefolder))

    @browsing
    def test_receipt_delivery_and_subdossier_column_are_hidden_in_document_tab(self, browser):
        browser.login().open(self.templatefolder, view=DOCUMENT_TAB)

        table_heading = browser.css('table.listing').first.lists()[0]
        self.assertEquals(['', 'Sequence Number', 'Title', 'Document Author',
                           'Document Date', 'Checked out by', 'Public Trial',
                           'Reference Number'],
                          table_heading)

    @browsing
    def test_receipt_delivery_and_subdossier_column_are_hidden_in_sablon_template_tab(self, browser):
        browser.login().open(self.templatefolder, view=SABLONTEMPLATES_TAB)

        table_heading = browser.css('table.listing').first.lists()[0]
        self.assertEquals(['', 'Sequence Number', 'Title', 'Document Author',
                           'Document Date', 'Checked out by', 'Public Trial',
                           'Reference Number'],
                          table_heading)

    @browsing
    def test_receipt_delivery_and_subdossier_column_are_hidden_in_proposal_templates_tab(self, browser):
        browser.login().open(self.templatefolder, view=PROPOSALTEMPLATES_TAB)

        table_heading = browser.css('table.listing').first.lists()[0]
        self.assertEquals(['', 'Sequence Number', 'Title', 'Document Author',
                           'Document Date', 'Checked out by', 'Public Trial',
                           'Reference Number'],
                          table_heading)

    @browsing
    def test_receipt_delivery_and_subdossier_column_are_hidden_in_trash_tab(self, browser):
        create(Builder('document').within(self.templatefolder).trashed())

        browser.login().open(self.templatefolder, view=TRASH_TAB)
        table_heading = browser.css('table.listing').first.lists()[0]
        self.assertEquals(['', 'Sequence Number', 'Title', 'Document Author',
                           'Document Date', 'Public Trial',
                           'Reference Number'],
                          table_heading)

    @browsing
    def test_enabled_actions_are_limited_in_document_tab(self, browser):
        browser.login().open(self.templatefolder, view=DOCUMENT_TAB)

        self.assertItemsEqual(
            ['Copy Items', 'Checkin with comment', 'Checkin without comment',
             'Export selection', 'Move Items', 'trashed', 'Export as Zip'],
            browser.css('.actionMenuContent li').text)

    @browsing
    def test_document_tab_lists_only_documents_directly_beneath(self, browser):
        subdossier = create(Builder('templatefolder')
                            .within(self.templatefolder))
        create(Builder('document').within(subdossier))

        browser.login().open(self.templatefolder, view=DOCUMENT_TAB)
        templates = browser.css('table.listing').first.dicts(as_text=False)
        self.assertEqual(1, len(templates))
        document_link = templates[0]['Title'].css('a').first.get('href')
        self.assertEqual(self.document.absolute_url(), document_link)

    @browsing
    def test_enabled_actions_are_limited_in_sablontemplates_tab(self, browser):
        browser.login().open(self.templatefolder, view=SABLONTEMPLATES_TAB)

        self.assertItemsEqual(
            ['Copy Items', 'Checkin with comment', 'Checkin without comment',
             'Export selection', 'trashed', 'Export as Zip'],
            browser.css('.actionMenuContent li').text)

    @browsing
    def test_enabled_actions_are_limited_in_proposaltemplates_tab(self, browser):
        browser.login().open(self.templatefolder, view=PROPOSALTEMPLATES_TAB)

        self.assertItemsEqual(
            ['Copy Items', 'Checkin with comment', 'Checkin without comment',
             'Export selection', 'trashed', 'Export as Zip'],
            browser.css('.actionMenuContent li').text)

    @browsing
    def test_sablontemplates_tab_lists_only_documents_directly_beneath(self, browser):
        subdossier = create(Builder('templatefolder')
                            .within(self.templatefolder))
        create(Builder('sablontemplate').within(subdossier))

        browser.login().open(self.templatefolder, view=SABLONTEMPLATES_TAB)
        templates = browser.css('table.listing').first.dicts(as_text=False)
        self.assertEqual(1, len(templates))
        template_link = templates[0]['Title'].css('a').first.get('href')
        self.assertEqual(self.template.absolute_url(), template_link)

    @browsing
    def test_proposaltemplates_tab_lists_only_documents_directly_beneath(self, browser):
        subdossier = create(Builder('templatefolder')
                            .within(self.templatefolder))
        create(Builder('proposaltemplate').within(subdossier))

        browser.login().open(self.templatefolder, view=PROPOSALTEMPLATES_TAB)
        templates = browser.css('table.listing').first.dicts(as_text=False)
        self.assertEqual(1, len(templates))
        template_link = templates[0]['Title'].css('a').first.get('href')
        self.assertEqual(self.proposaltemplate.absolute_url(), template_link)

    @browsing
    def test_trash_tab_lists_only_documents_directly_beneath(self, browser):
        trashed = create(
            Builder('document').trashed().within(self.templatefolder))
        subdossier = create(Builder('templatefolder')
                            .within(self.templatefolder))
        create(Builder('document').trashed().within(subdossier))

        browser.login().open(self.templatefolder, view=TRASH_TAB)
        templates = browser.css('table.listing').first.dicts(as_text=False)
        self.assertEqual(1, len(templates))
        trashed_link = templates[0]['Title'].css('a').first.get('href')
        self.assertEqual(trashed.absolute_url(), trashed_link)


class TestTemplateDocumentTabs(FunctionalTestCase):

    def setUp(self):
        super(TestTemplateDocumentTabs, self).setUp()

        self.templatefolder = create(Builder('templatefolder'))
        self.template = create(Builder('document')
                               .within(self.templatefolder)
                               .titled('My Document'))

    @browsing
    def test_template_overview_tab(self, browser):
        browser.login().open(self.template, view=OVERVIEW_TAB)
        table = browser.css('table.listing').first
        self.assertIn(['Title', 'My Document'], table.lists())

    @browsing
    def test_template_journal_tab(self, browser):
        browser.login().open(self.template, view=JOURNAL_TAB)
        journal_entries = browser.css('table.listing').first.dicts()
        self.assertEqual(Actor.lookup(TEST_USER_ID).get_label(),
                         journal_entries[0]['Changed by'])
        self.assertEqual('Document added: My Document',
                         journal_entries[0]['Title'])

    @browsing
    def test_template_info_tab(self, browser):
        # we want to test authenticated user, which only a Manager can see
        self.grant('Manager')
        browser.login()

        browser.open(self.template, view=INFO_TAB)
        self.assertEquals([['Logged-in users', False, False, False]],
                          sharing_tab_data())

        self.template.manage_setLocalRoles(TEST_USER_ID,
                                           ["Reader", "Contributor", "Editor"])
        transaction.commit()

        browser.open(self.template, view=INFO_TAB)
        self.assertEquals([['Logged-in users', False, False, False],
                           ['test-user (test_user_1_)', True, True, True]],
                          sharing_tab_data())


class TestDossierTemplateFeature(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_DOSSIER_TEMPLATE_LAYER

    @browsing
    def test_dossier_template_is_addable_if_dossier_template_feature_is_enabled(self, browser):
        templatefolder = create(Builder('templatefolder'))
        browser.login().open(templatefolder)

        self.assertIn('Dossier template', factoriesmenu.addable_types())

    @browsing
    def test_show_dossier_templates_tab(self, browser):
        templatefolder = create(Builder('templatefolder'))

        browser.login().visit(templatefolder)

        self.assertEqual(
            'Dossier templates',
            browser.css('.formTab #tab-dossiertemplates').first.text)

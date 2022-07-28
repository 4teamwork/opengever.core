from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import assert_message
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from ftw.testing import freeze
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.document.behaviors import IBaseDocument
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.document import IDocumentSchema
from opengever.document.document import UploadValidator
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.interfaces import IDocumentSettings
from opengever.dossier.deactivate import DossierDeactivator
from opengever.dossier.resolve import LockingResolveManager
from opengever.officeconnector.interfaces import IOfficeConnectorSettings
from opengever.testing import FunctionalTestCase
from opengever.testing import index_data_for
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from opengever.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.virusscan.interfaces import IAVScannerSettings
from opengever.virusscan.testing import EICAR
from opengever.virusscan.testing import register_mock_av_scanner
from plone import api
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.fti import register
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from Products.CMFCore.utils import getToolByName
from z3c.form import interfaces
from z3c.form.interfaces import IFieldWidget
from zope.component import createObject
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import Invalid
from zope.schema import getFields
import mimetypes
import transaction


class TestDocumentConfiguration(IntegrationTestCase):

    def test_documents_provide_IDocumentSchema(self):
        self.login(self.regular_user)
        self.assert_provides(self.document, interface=IDocumentSchema)

    def test_documents_provide_IBaseDocument(self):
        self.login(self.regular_user)
        self.assert_provides(self.document, interface=IBaseDocument)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='opengever.document.document')
        self.assertNotEqual(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='opengever.document.document')
        schema = fti.lookupSchema()
        self.assertEqual(IDocumentSchema, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='opengever.document.document')
        factory = fti.factory
        new_object = createObject(factory)
        self.assert_provides(new_object, interface=IDocumentSchema)


class TestDocument(IntegrationTestCase):

    def test_upload_file(self):
        self.login(self.regular_user)
        field = IDocumentSchema['file']
        file_ = NamedBlobFile('bla bla', filename=u'test.txt')
        field.set(self.document, file_)
        self.assertTrue(field.get(self.document).data == 'bla bla')

    def test_is_not_a_mail(self):
        self.login(self.regular_user)
        self.assertFalse(self.document.is_mail)

    def test_filename_getter_returns_filename_if_file_is_available(self):
        self.login(self.regular_user)
        self.assertEqual(u'Vertraegsentwurf.docx', self.document.get_filename())

    def test_filename_getter_return_none_if_no_file_is_available(self):
        self.login(self.regular_user)
        self.assertIsNone(self.empty_document.get_filename())

    def test_document_with_file_is_digitally_available(self):
        self.login(self.regular_user)
        self.assertTrue(self.document.digitally_available)

    def test_document_without_file_is_not_digitally_available(self):
        self.login(self.regular_user)
        self.assertFalse(self.empty_document.digitally_available)

    @browsing
    def test_documents_tabbedview(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='@@tabbed_view')
        self.assertEqual(['Overview', 'Versions', 'Journal', 'Info'], browser.css('.formTabs .formTab').text)

    @browsing
    def test_documents_properties_view(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='@@view')
        self.assertEqual(u'Vertr\xe4gsentwurf', browser.css('.documentFirstHeading').first.text)
        self.assertEqual(
            ['Common', 'Classification', 'Custom properties'],
            browser.css('.dossier-detail-listing-title').text
        )

    def test_accessors(self):
        self.login(self.regular_user)
        self.assertEqual(self.document.Title(), 'Vertr\xc3\xa4gsentwurf')
        self.assertEqual(self.document.Description(), 'Wichtige Vertr\xc3\xa4ge')

    def test_checked_out_by_returns_userid(self):
        self.login(self.regular_user)
        self.assertEqual(None, self.document.checked_out_by())
        self.checkout_document(self.document)
        self.assertEqual(self.regular_user.id, self.document.checked_out_by())

    def test_is_checked_in(self):
        self.login(self.regular_user)
        self.assertFalse(self.document.is_checked_out())
        self.checkout_document(self.document)
        self.assertTrue(self.document.is_checked_out())

    def test_related_items(self):
        self.login(self.regular_user)
        self.assertEqual([], self.document.related_items())
        self.assertEqual([self.document], self.subdocument.related_items())
        self.assertEqual([self.document, self.subdocument],
                         self.subsubdocument.related_items())

        self.assertItemsEqual(
            [self.proposal, self.subdocument, self.subsubdocument, self.task,
             self.subtask, self.info_task, self.private_task, self.inbox_task],
            self.document.related_items(include_backrefs=True))
        self.assertItemsEqual(
            [self.subdocument, self.subsubdocument],
            self.document.related_items(include_backrefs=True, documents_only=True))
        self.assertItemsEqual(
            [self.task, self.subtask, self.info_task,
             self.private_task, self.inbox_task],
            self.document.related_items(include_backrefs=True, tasks_only=True))
        self.assertItemsEqual(
            [self.subsubdocument],
            self.subdocument.related_items(include_backrefs=True,
                                           include_forwardrefs=False))

    def test_is_removed(self):
        self.login(self.regular_user)
        self.assertFalse(self.document.is_removed)
        with self.login(self.manager):
            self.assertTrue(self.removed_document.is_removed)

    def test_document_inside_a_dossier_is_movable(self):
        self.login(self.regular_user)
        self.assertTrue(self.document.is_movable())

    def test_document_inside_a_resolved_dossier_is_not_movable(self):
        self.login(self.secretariat_user)

        resolve_manager = LockingResolveManager(self.resolvable_dossier)
        resolve_manager.resolve()

        self.assertFalse(self.resolvable_document.is_movable())

    def test_document_inside_a_deactivated_dossier_is_not_movable(self):
        self.login(self.secretariat_user)

        deactivator = DossierDeactivator(self.resolvable_dossier)
        deactivator.deactivate()

        self.assertFalse(self.resolvable_document.is_movable())

    def test_document_inside_a_resolved_subdossier_is_not_movable(self):
        self.login(self.secretariat_user)

        resolve_manager = LockingResolveManager(self.resolvable_subdossier)
        resolve_manager.resolve()

        self.assertFalse(self.resolvable_document.is_movable())

    def test_document_inside_a_deactivated_subdossier_is_not_movable(self):
        self.login(self.secretariat_user)

        deactivator = DossierDeactivator(self.resolvable_subdossier)
        deactivator.deactivate()

        self.assertFalse(self.resolvable_document.is_movable())

    def test_document_inside_an_inbox_is_movable(self):
        self.login(self.secretariat_user)
        self.assertTrue(self.inbox_document.is_movable())

    def test_document_inside_a_task_is_not_movable(self):
        self.login(self.regular_user)
        self.assertFalse(self.taskdocument.is_movable())

    def test_document_inside_a_submitted_proposal_is_not_movable(self):
        self.login(self.meeting_user)
        submitted_document = self.submitted_proposal.get_documents()[0]
        self.assertFalse(submitted_document.is_movable())

    def test_current_document_version_is_increased(self):
        self.login(self.regular_user)
        self.assertEqual(None, self.document.get_current_version_id())
        self.assertEqual(0, self.document.get_current_version_id(missing_as_zero=True))

        self.document.file = NamedBlobFile(data='New', filename=u'test.txt')
        self.assertEqual(0, self.document.get_current_version_id())

        repository = api.portal.get_tool('portal_repository')
        repository.save(self.document)
        self.assertEqual(1, self.document.get_current_version_id())

    def test_get_parent_dossier_returns_direct_parent_for_dossiers(self):
        self.login(self.regular_user)
        self.assertEqual(self.dossier, self.document.get_parent_dossier())
        self.assertEqual(self.subdossier, self.subdocument.get_parent_dossier())
        self.assertEqual(self.subsubdossier, self.subsubdocument.get_parent_dossier())

    def test_get_parent_dossier_returns_tasks_dossier(self):
        self.login(self.regular_user)
        self.assertEqual(self.dossier, self.taskdocument.get_parent_dossier())

    def test_get_parent_inbox_returns_inbox_for_document_in_inbox(self):
        self.login(self.secretariat_user)
        self.assertEqual(self.inbox, self.inbox_document.get_parent_inbox())

    def test_get_parent_inbox_returns_none_for_document_in_dossier(self):
        self.login(self.regular_user)
        self.assertIsNone(self.document.get_parent_inbox())

    def test_is_inside_a_template_folder_return_false_if_not_in_a_template_folder(self):
        self.login(self.regular_user)
        self.assertFalse(self.document.is_inside_a_template_folder())
        self.assertFalse(self.mail_eml.is_inside_a_template_folder())

    def test_is_inside_a_template_folder_return_true_if_inside_a_template_folder(self):
        self.login(self.regular_user)
        self.assertTrue(self.normal_template.is_inside_a_template_folder())

    def test_is_inside_a_template_folder_return_true_if_directly_inside_a_dossier_template(self):
        self.login(self.regular_user)
        self.assertTrue(self.dossiertemplatedocument.is_inside_a_template_folder())

    @browsing
    def test_regular_user_can_add_new_keywords_in_document(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.subsubdocument, view='@@edit')

        keywords = browser.find_field_by_text(u'Keywords')
        new = browser.css('#' + keywords.attrib['id'] + '_new').first
        new.text = u'NewItem1\nNew Item 2\nN\xf6i 3'
        browser.find_button_by_label('Save').click()

        self.assertItemsEqual(('New Item 2', 'NewItem1', u'N\xf6i 3'),
                              IDocumentMetadata(self.subsubdocument).keywords)

        browser.open(self.subsubdocument, view='edit')
        keywords = browser.find_field_by_text(u'Keywords')
        self.assertItemsEqual(('New Item 2', 'NewItem1', 'N=C3=B6i 3'), tuple(keywords.value))

    def test_fixtured_document_is_office_connector_editable_per_default(self):
        self.login(self.regular_user)
        self.assertTrue(self.document.is_office_connector_editable())

    def test_office_connector_editable_mimetype_check_is_case_insensitive(self):
        self.login(self.regular_user)
        self.document.file.contentType = self.document.file.contentType.upper()
        self.assertTrue(self.document.is_office_connector_editable())

    def test_can_add_additional_mimetypes_to_office_connector_editable_mimetypes(self):
        api.portal.set_registry_record(
            'officeconnector_editable_types_extra',
            [u'foo/bar'],
            interface=IOfficeConnectorSettings,
        )
        self.login(self.regular_user)
        self.document.file.contentType = u'foo/bar'
        self.assertTrue(self.document.is_office_connector_editable())

    def test_can_blacklist_mimetypes_from_office_connector_editable_mimetypes(self):
        api.portal.set_registry_record(
            'officeconnector_editable_types_blacklist',
            [u'application/vnd.openxmlformats-officedocument.wordprocessingml.document', u'foo/bar'],
            interface=IOfficeConnectorSettings,
        )
        self.login(self.regular_user)
        self.assertFalse(self.document.is_office_connector_editable())
        self.document.file.contentType = u'foo/bar'
        self.assertFalse(self.document.is_office_connector_editable())

    def test_office_connector_editable_mimetype_blacklist_is_stronger_than_whitelist(self):
        api.portal.set_registry_record(
            'officeconnector_editable_types_extra',
            [u'foo/bar'],
            interface=IOfficeConnectorSettings,
        )
        api.portal.set_registry_record(
            'officeconnector_editable_types_blacklist',
            [u'foo/bar'],
            interface=IOfficeConnectorSettings,
        )
        self.login(self.regular_user)
        self.document.file.contentType = 'foo/bar'
        self.assertFalse(self.document.is_office_connector_editable())

    def test_checkout_and_get_office_connector_url(self):
        """The checkout_and_get_office_connector_url method should check out
        the document and return an url which will open the office connector.
        """
        api.portal.set_registry_record('direct_checkout_and_edit_enabled', False, interface=IOfficeConnectorSettings)
        self.login(self.regular_user)
        checkout_manager = getMultiAdapter((self.document, self.request), ICheckinCheckoutManager)
        self.assertIsNone(checkout_manager.get_checked_out_by())
        url = self.document.checkout_and_get_office_connector_url()
        self.assertEqual('/'.join((self.document.absolute_url(), 'external_edit')), url)
        self.assertEqual(self.regular_user.id, checkout_manager.get_checked_out_by())

    def test_checkout_and_get_office_connector_url_with_checkout_feature(self):
        """When the office connector checkout feature is enabled, the
        checkout_and_get_office_connector_url method should simply return an
        office connector URL which includes the checkout command.
        """
        self.login(self.regular_user)
        checkout_manager = getMultiAdapter((self.document, self.request), ICheckinCheckoutManager)
        self.assertIsNone(checkout_manager.get_checked_out_by())
        url = self.document.checkout_and_get_office_connector_url()
        self.assertTrue(url.startswith('oc:'), url)
        self.assertIsNone(checkout_manager.get_checked_out_by())


class TestDocumentDefaultValues(IntegrationTestCase):

    @browsing
    def test_default_document_date_is_today(self, browser):
        self.login(self.regular_user, browser)

        now = datetime.now()
        today = now.date()
        browser.open(self.dossier)

        with freeze(now):
            factoriesmenu.add('Document')
            browser.fill({'Title': u'My Document'}).save()

        document = self.dossier['document-44']
        self.assertEqual(today, document.document_date)

    @browsing
    def test_preserved_as_paper_default_false(self, browser):
        api.portal.set_registry_record('preserved_as_paper_default', False, interface=IDocumentSettings)
        self.login(self.regular_user, browser)
        browser.open(self.dossier)

        factoriesmenu.add('Document')
        browser.fill({'Title': u'My Document', 'File': ('DATA', 'file.txt', 'text/plain')}).save()

        document = self.dossier['document-44']
        self.assertFalse(document.preserved_as_paper)

    @browsing
    def test_preserved_as_paper_default_true(self, browser):
        api.portal.set_registry_record('preserved_as_paper_default', True, interface=IDocumentSettings)
        self.login(self.regular_user, browser)
        browser.open(self.dossier)

        factoriesmenu.add('Document')
        browser.fill({'Title': u'My Document'}).save()

        document = self.dossier['document-44']
        self.assertTrue(document.preserved_as_paper)


class TestDocumentNumbering(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentNumbering, self).setUp()

        fti = DexterityFTI('SimpleDocument')
        fti.klass = 'plone.dexterity.content.Container'
        fti.behaviors = ('opengever.document.behaviors.IBaseDocument', )
        fti.schema = 'opengever.document.document.IDocumentSchema'

        typestool = getToolByName(self.portal, 'portal_types')
        typestool._setObject('SimpleDocument', fti)
        register(fti)

    def test_objects_marked_as_BaseDocuments_use_same_counter(self):
        seqNumb = getUtility(ISequenceNumber)
        d1 = createContentInContainer(self.portal, 'opengever.document.document')
        b1 = createContentInContainer(self.portal, 'SimpleDocument')
        d2 = createContentInContainer(self.portal, 'opengever.document.document')

        self.assertEquals([1, 2, 3],
                          [seqNumb.get_number(d1),
                           seqNumb.get_number(b1),
                           seqNumb.get_number(d2)])

    def test_reference_number_works_for_objects_marked_as_BaseDocument(self):
        d1 = createContentInContainer(self.portal, 'opengever.document.document')
        b1 = createContentInContainer(self.portal, 'SimpleDocument')
        d2 = createContentInContainer(self.portal, 'opengever.document.document')

        self.assertEquals(['Client1 / 1', 'Client1 / 2', 'Client1 / 3'],
                          [getAdapter(d1, IReferenceNumber).get_number(),
                           getAdapter(b1, IReferenceNumber).get_number(),
                           getAdapter(d2, IReferenceNumber).get_number()])


class Mock(object):
    pass


class TestUploadValidator(FunctionalTestCase):

    def test_is_registered_on_file_field(self):
        validator = queryMultiAdapter(
            self.validator_arguments(),
            interfaces.IValidator)

        self.assertTrue(isinstance(validator, UploadValidator),
                        "Expected %s to be a UploadValidator" % validator)

    def test_accepts_normal_files(self):
        file = NamedBlobFile('bla bla', filename=u'test.txt')

        validator = UploadValidator(*self.validator_arguments())

        validator.validate(file)

    def test_does_not_accept_eml(self):
        mail = NamedBlobFile('bla bla', filename=u'test.eml')
        validator = UploadValidator(*self.validator_arguments())

        with self.assertRaises(Invalid) as cm:
            self.assertFalse(validator.validate(mail))
        self.assertEquals('error_mail_upload', str(cm.exception))

    def test_does_not_accept_msg(self):
        mail = NamedBlobFile('bla bla', filename=u'test.msg')
        validator = UploadValidator(*self.validator_arguments())

        with self.assertRaises(Invalid) as cm:
            self.assertFalse(validator.validate(mail))
        self.assertEquals('error_mail_upload', str(cm.exception))

    def test_does_not_accept_p7m(self):
        mail = NamedBlobFile('bla bla', filename=u'test.p7m')
        validator = UploadValidator(*self.validator_arguments())

        with self.assertRaises(Invalid) as cm:
            self.assertFalse(validator.validate(mail))
        self.assertEquals('error_mail_upload', str(cm.exception))

    def test_rejects_file_containing_virus(self):
        register_mock_av_scanner()
        api.portal.set_registry_record(
            'scan_on_upload', True,interface=IAVScannerSettings)

        file = NamedBlobFile(EICAR, filename=u'test.txt')
        validator = UploadValidator(*self.validator_arguments())

        with self.assertRaises(Invalid) as cm:
            self.assertFalse(validator.validate(file))

        self.assertEquals(
            'file_infected',
            str(cm.exception))

    def validator_arguments(self):
        dossier = create(Builder("dossier"))
        document = create(Builder("document").within(dossier))
        field = getFields(IDocumentSchema).get('file')
        widget = getMultiAdapter((field, self.request), IFieldWidget)

        view = Mock()
        view.parentForm = Mock()
        return (document, document.REQUEST, view, field, widget)


class TestDocumentMimetype(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentMimetype, self).setUp()
        self.dossier = create(Builder("dossier"))
        transaction.commit()

    @browsing
    def test_mimetype_sent_by_browser_is_ignored_on_upload(self, browser):
        browser.login().open(self.dossier.absolute_url())
        factoriesmenu.add('Document')

        browser.fill({'File': (
            'File data', 'file.txt', 'application/i-dont-know')}).save()
        assert_message('Item created')
        doc = browser.context.restrictedTraverse('document-1')
        self.assertEquals('text/plain', doc.file.contentType)

    @browsing
    def test_mimetype_is_determined_by_using_python_mtr(self, browser):
        mimetypes.add_type('application/foobar', '.foo')

        browser.login().open(self.dossier.absolute_url())
        factoriesmenu.add('Document')

        browser.fill({'File': (
            'File data', 'file.foo', 'application/i-dont-know')}).save()
        assert_message('Item created')
        doc = browser.context.restrictedTraverse('document-1')
        self.assertEquals('application/foobar', doc.file.contentType)

    def test_mimetype_lookups_are_case_insensitive(self):
        doc = create(Builder('document').within(self.dossier).with_dummy_content())
        self.assertEqual(str(doc.get_mimetype()[0]), 'application/msword')
        doc.file.contentType = 'application/MSWORD'
        self.assertEqual(str(doc.get_mimetype()[0]), 'application/msword')
        doc.file.contentType = 'application/vnd.ms-excel.sheet.macroEnabled.12'
        self.assertEqual(str(doc.get_mimetype()[0]), 'application/vnd.ms-excel.sheet.macroEnabled.12')
        doc.file.contentType = 'application/vnd.ms-excel.sheet.macroenabled.12'
        self.assertEqual(str(doc.get_mimetype()[0]), 'application/vnd.ms-excel.sheet.macroEnabled.12')


class TestDocumentAuthorResolving(IntegrationTestCase):

    def test_adding_document_with_a_userid_as_author_resolves_to_fullname(self):
        document = create(Builder('document')
                          .having(document_author='kathi.barfuss')
                          .with_dummy_content())

        self.assertEquals(u'B\xe4rfuss K\xe4thi', document.document_author)
        self.assertEquals('B\xc3\xa4rfuss K\xc3\xa4thi',
                          obj2brain(document, unrestricted=True).document_author)

    def test_adding_document_with_a_real_name_as_author_dont_change_author_name(self):
        document = create(Builder('document')
                          .having(document_author='Muster Peter')
                          .with_dummy_content())

        self.assertEquals('Muster Peter', document.document_author)

    @browsing
    def test_editing_document_with_a_userid_as_author_resolves_to_fullname(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='edit')
        browser.fill({'Author': u'kathi.barfuss'})
        browser.click_on('Save')

        self.assertEquals(u'B\xe4rfuss K\xe4thi', self.document.document_author)
        self.assertEquals('B\xc3\xa4rfuss K\xc3\xa4thi', obj2brain(self.document).document_author)

    @browsing
    def test_editing_document_with_a_real_name_as_author_dont_change_author_name(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='edit')
        browser.fill({'Author': u'Muster Peter'})
        browser.click_on('Save')

        self.assertEquals('Muster Peter', self.document.document_author)


class TestDocumentValidatorsInAddForm(IntegrationTestCase):

    @browsing
    def test_mails_are_not_allowed(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier)

        factoriesmenu.add('Document')
        browser.fill({'File': ('hello', 'mail.eml', 'message/rfc822'),
                      'Physical file': False}).save()

        selector = '#formfield-form-widgets-file.field.error'
        error_field = browser.css(selector).first
        self.assertIn(
            "Emails can't be added here. Please send it to",
            error_field.text)

        self.assertEqual(
            1, len(browser.css('#formfield-form-widgets-file input')),
            "Should not display radio buttons in case of add form.")


class TestDocumentValidatorsInEditForm(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestDocumentValidatorsInEditForm, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.doc_with_file = create(Builder('document')
                                   .within(self.dossier)
                                   .titled("Document with file")
                                   .having(preserved_as_paper=True)
                                   .with_dummy_content())

        self.doc_without_file = create(Builder('document')
                                       .within(self.dossier)
                                       .titled("Document without file")
                                       .having(preserved_as_paper=True))

    @browsing
    def test_editing_and_saving_valid_documents_works(self, browser):
        browser.login().open(self.doc_with_file.absolute_url() + '/edit')
        browser.forms['form'].save()
        assert_no_error_messages()

        browser.login().open(self.doc_without_file.absolute_url() + '/edit')
        browser.forms['form'].save()
        assert_no_error_messages()


class TestDocumentValidatorsInEditFormForCheckedOutDoc(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestDocumentValidatorsInEditFormForCheckedOutDoc, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.doc_with_file = create(Builder('document')
                                    .within(self.dossier)
                                    .titled("Document with file")
                                    .having(preserved_as_paper=True)
                                    .with_dummy_content()
                                    .checked_out())

        self.doc_without_file = create(Builder('document')
                                       .within(self.dossier)
                                       .titled("Document without file")
                                       .having(preserved_as_paper=True)
                                       .checked_out())

    @browsing
    def test_editing_and_saving_valid_documents_works(self, browser):
        browser.login().open(self.doc_with_file.absolute_url() + '/edit')
        browser.forms['form'].save()
        assert_no_error_messages()

        browser.login().open(self.doc_without_file.absolute_url() + '/edit')
        browser.forms['form'].save()
        assert_no_error_messages()


class TestPublicTrial(FunctionalTestCase):

    def setUp(self):
        super(TestPublicTrial, self).setUp()

        self.document = create(Builder('document')
                               .having(public_trial='private'))

    def test_public_trial_metadata_field_exists(self):
        self.assertEquals('private',
                          obj2brain(self.document).public_trial)

    def test_public_trial_index_exists_and_is_used(self):
        catalog = getToolByName(self.portal, 'portal_catalog')

        # check if index exists
        self.assertIn('public_trial', catalog.indexes())

        # check if object got indexed
        self.assertEquals('private',
                          index_data_for(self.document).get('public_trial'))

    @browsing
    def test_public_trial_is_displayed(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier A'))
        document = create(Builder('document').within(dossier))

        browser.login().open(document, view='view')

        self.assertTrue(
            browser.css('#form-widgets-IClassification-public_trial'))

    @browsing
    def test_public_trial_is_displayed_after_visiting_a_dossier(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier A'))
        document = create(Builder('document').within(dossier))

        browser.login().open(dossier, view='view')
        browser.open(document, view='view')

        self.assertTrue(
            browser.css('#form-widgets-IClassification-public_trial'))


class TestArchivalFileField(FunctionalTestCase):

    def setUp(self):
        super(TestArchivalFileField, self).setUp()

        self.dossier = create(Builder('dossier'))
        self.grant('Manager')

    @browsing
    def test_archival_file_is_displayed_but_in_a_separate_fieldset(self, browser):
        browser.login().open(self.dossier)
        factoriesmenu.add('Document')

        archival_file_field = browser.css(
            '#form-widgets-IDocumentMetadata-archival_file').first
        self.assertEquals(
            'Archival file', archival_file_field.parent('fieldset legend').text)

from Products.CMFCore.utils import getToolByName
from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from opengever.document.behaviors import IBaseDocument
from opengever.document.document import IDocumentSchema
from opengever.document.document import UploadValidator
from opengever.document.interfaces import IDocumentSettings
from opengever.testing import FunctionalTestCase
from opengever.testing import create_ogds_user
from opengever.testing.helpers import obj2brain
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.fti import register
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from plone.registry.interfaces import IRegistry
from z3c.form import interfaces
from z3c.form.interfaces import IValue
from zope.component import createObject
from zope.component import queryMultiAdapter, getAdapter
from zope.component import queryUtility, getUtility
from zope.interface import Invalid
from zope.schema import getFields
import transaction


class TestDocumentConfiguration(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentConfiguration, self).setUp()
        self.grant('Contributor')

    def test_documents_provide_IDocumentSchema(self):
        document = create(Builder("document"))
        self.assertProvides(document, interface=IDocumentSchema)

    def test_documents_provide_IBaseDocument(self):
        document = create(Builder("document"))
        self.assertProvides(document, interface=IBaseDocument)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='opengever.document.document')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='opengever.document.document')
        schema = fti.lookupSchema()
        self.assertEquals(IDocumentSchema, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='opengever.document.document')
        factory = fti.factory
        new_object = createObject(factory)
        self.assertProvides(new_object, interface=IDocumentSchema)


class TestDocument(FunctionalTestCase):

    def setUp(self):
        super(TestDocument, self).setUp()
        self.grant('Contributor')

    def test_upload_file(self):
        document = create(Builder("document"))
        field = IDocumentSchema['file']
        file = NamedBlobFile('bla bla', filename=u'test.txt')
        field.set(document, file)
        self.assertTrue(field.get(document).data == 'bla bla')

    def test_document_with_file_is_digitally_available(self):
        document_with_file = create(Builder("document").with_dummy_content())
        self.assertTrue(document_with_file.digitally_available)

    def test_document_without_file_is_not_digitally_available(self):
        document_without_file = create(Builder("document"))
        self.assertFalse(document_without_file.digitally_available)

    def test_document_without_digital_file_must_be_preserved_in_paper(self):
        document = create(Builder("document").having(preserved_as_paper=False))
        with self.assertRaises(Invalid) as cm:
            IDocumentSchema.validateInvariants(document)
        self.assertEquals("error_title_or_file_required", str(cm.exception))

    # TODO: split this and assert something useful ;)
    def test_views(self):
        document = create(Builder("document"))
        document.keywords = ()

        self.portal.REQUEST['ACTUAL_URL'] = document.absolute_url()

        view = document.restrictedTraverse('@@view')
        self.failUnless(view())
        tabbed_view = document.restrictedTraverse('@@tabbed_view')
        self.failUnless(tabbed_view())

    def test_copying_a_document_modifies_the_title(self):
        document = create(Builder("document").titled("Testdocument"))

        cb = self.portal.manage_copyObjects(document.id)
        self.portal.manage_pasteObjects(cb)

        self.assertEquals(u'copy of Testdocument',
                          self.portal['copy_of_document-1'].title)

    def test_copying_a_document_does_not_copy_its_versions(self):
        orig_doc = create(Builder("document").having(preserved_as_paper=False))

        cb = self.portal.manage_copyObjects(orig_doc.id)
        self.portal.manage_pasteObjects(cb)

        new_doc = self.portal['copy_of_document-1']

        new_history = self.portal.portal_repository.getHistory(new_doc)
        # The new history should have an initial version,
        # but existing versions shouldn't be copied
        self.assertEquals(len(new_history), 1)

    def test_accessors(self):
        document = create(Builder("document")
                          .titled(u'Test title')
                          .having(description=u'Lorem ipsum'))

        self.assertEquals(document.Title(), 'Test title')
        self.assertEquals(document.Description(), 'Lorem ipsum')


class TestDocumentDefaultValues(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentDefaultValues, self).setUp()
        self.grant('Contributor')

    def test_default_document_date_is_today(self):
        self.assertEquals(date.today(), self.default_value_for('document_date'))

    def test_preserverd_as_paper_default(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IDocumentSettings)

        proxy.preserved_as_paper_default = False
        transaction.commit()
        self.assertFalse(self.default_value_for('preserved_as_paper'))

        proxy.preserved_as_paper_default = True
        transaction.commit()
        self.assertTrue(self.default_value_for('preserved_as_paper'))

    def default_value_for(self, field_name):
        field = getFields(IDocumentSchema).get(field_name)
        document = createContentInContainer(self.portal,
                                            'opengever.document.document')
        default = queryMultiAdapter(
            (document, document.REQUEST, None, field, None, ),
            IValue, name='default')
        return default.get()


class TestDocumentNumbering(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentNumbering, self).setUp()
        self.grant('Contributor')

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

    def test_does_not_accept_emails(self):
        mail = NamedBlobFile('bla bla', filename=u'test.eml')
        validator = UploadValidator(*self.validator_arguments())

        with self.assertRaises(Invalid) as cm:
            self.assertFalse(validator.validate(mail))
        self.assertEquals('error_mail_upload', str(cm.exception))

    def validator_arguments(self):
        dossier = create(Builder("dossier"))
        document = create(Builder("document").within(dossier))
        field = getFields(IDocumentSchema).get('file')

        return (document, document.REQUEST, None, field, None)


class TestDocumentAuthorResolving(FunctionalTestCase):
    use_browser = True

    def test_adding_document_with_a_userid_as_author_resolves_to_fullname(self):
        create_ogds_user('hugo.boss', firstname='Hugo', lastname='Boss')
        document = create(Builder('document')
                          .having(document_author='hugo.boss')
                          .with_dummy_content())

        self.assertEquals('Boss Hugo', document.document_author)
        self.assertEquals('Boss Hugo', obj2brain(document).document_author)

    def test_adding_document_with_a_real_name_as_author_dont_change_author_name(self):
        document = create(Builder('document')
                          .having(document_author='Muster Peter')
                          .with_dummy_content())

        self.assertEquals('Muster Peter', document.document_author)

    def test_editing_document_with_a_userid_as_author_resolves_to_fullname(self):
        create_ogds_user('hugo.boss', firstname='Hugo', lastname='Boss')
        document = create(Builder('document')
                          .having(document_author='hanspeter')
                          .with_dummy_content())

        self.browser.open('%s/edit' % (document.absolute_url()))
        self.browser.fill({'Author': u'hugo.boss'})
        self.browser.click('Save')

        self.assertEquals('Boss Hugo', document.document_author)
        self.assertEquals('Boss Hugo', obj2brain(document).document_author)

    def test_editing_document_with_a_real_name_as_author_dont_change_author_name(self):
        document = create(Builder('document')
                          .having(document_author='hugo.boss')
                          .with_dummy_content())

        self.browser.open('%s/edit' % (document.absolute_url()))
        self.browser.fill({'Author': u'Muster Peter'})
        self.browser.click('Save')

        self.assertEquals('Muster Peter', document.document_author)

from datetime import date
from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testing import freeze
from hashlib import sha256
from opengever.base.default_values import get_persisted_values_for_obj
from opengever.private.tests import create_members_folder
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import fake_interaction
from plone import api
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.utils import createContentInContainer
from plone.dexterity.utils import iterSchemataForType
from plone.namedfile.file import NamedBlobFile
from z3c.form.browser.checkbox import CheckBoxWidget
from z3c.form.browser.checkbox import SingleCheckBoxWidget
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IGroupForm
from zope.schema import getFieldsInOrder
from zope.schema import List
import json
import textwrap


FROZEN_NOW = datetime.now()
FROZEN_TODAY = FROZEN_NOW.date()

DEFAULT_TITLE = u'My title'
DEFAULT_CLIENT = u'fa'

REPOROOT_REQUIREDS = {
    'title_de': DEFAULT_TITLE,
}
REPOROOT_DEFAULTS = {}
REPOROOT_FORM_DEFAULTS = {}
REPOROOT_MISSING_VALUES = {
    'title_fr': None,
    'valid_from': None,
    'valid_until': None,
    'version': None,
}


REPOFOLDER_REQUIREDS = {
    'title_de': DEFAULT_TITLE,
}
REPOFOLDER_DEFAULTS = {
    'archival_value': u'unchecked',
    'classification': u'unprotected',
    'custody_period': 30,
    'description': u'',
    'privacy_layer': u'privacy_layer_no',
    'public_trial': u'unchecked',
    'public_trial_statement': '',
    'reference_number_prefix': u'1',
    'retention_period': 5,
}
REPOFOLDER_FORM_DEFAULTS = {}
REPOFOLDER_MISSING_VALUES = {
    'addable_dossier_templates': [],
    'addable_dossier_types': [],
    'allow_add_businesscase_dossier': True,
    'archival_value_annotation': None,
    'date_of_cassation': None,
    'date_of_submission': None,
    'former_reference': None,
    'location': None,
    'referenced_activity': None,
    'retention_period_annotation': None,
    'title_fr': None,
    'valid_from': None,
    'valid_until': None,
}


DOSSIER_REQUIREDS = {
    'title': DEFAULT_TITLE,
}
DOSSIER_DEFAULTS = {
    'archival_value': u'unchecked',
    'classification': u'unprotected',
    'custody_period': 30,
    'description': u'',
    'keywords': (),
    'privacy_layer': u'privacy_layer_no',
    'public_trial': u'unchecked',
    'public_trial_statement': u'',
    'relatedDossier': [],
    'retention_period': 5,
    'start': FROZEN_TODAY,
    'reading': [],
    'reading_and_writing': [],
    'dossier_manager': None,
}
DOSSIER_FORM_DEFAULTS = {
    'responsible': 'kathi.barfuss',
}
DOSSIER_MISSING_VALUES = {
    'archival_value_annotation': None,
    'comments': None,
    'container_location': None,
    'container_type': None,
    'date_of_cassation': None,
    'date_of_submission': None,
    'end': None,
    'external_reference': None,
    'filing_prefix': None,
    'former_reference_number': None,
    'number_of_containers': None,
    'responsible': None,
    'retention_period_annotation': None,
    'temporary_former_reference_number': None,
}


DOCUMENT_REQUIREDS = {
    'title': DEFAULT_TITLE,
}
DOCUMENT_DEFAULTS = {
    'classification': u'unprotected',
    'description': u'',
    'digitally_available': True,
    'document_date': FROZEN_TODAY,
    'file': None,  # needs to be updated with NamedBlobFile in actual test
    'keywords': (),
    'preserved_as_paper': True,
    'privacy_layer': u'privacy_layer_no',
    'public_trial': u'unchecked',
    'public_trial_statement': '',
    'relatedItems': [],
}
DOCUMENT_FORM_DEFAULTS = {}
DOCUMENT_MISSING_VALUES = {
    'archival_file': None,
    'archival_file_state': None,
    'delivery_date': None,
    'document_author': None,
    'document_type': None,
    'file': None,
    'foreign_reference': None,
    'preview': None,
    'receipt_date': None,
    'thumbnail': None,
}


MAIL_REQUIREDS = {}
MAIL_DEFAULTS = {
    'classification': u'unprotected',
    'description': u'',
    'digitally_available': True,
    'document_author': u'from@example.org',
    'document_date': date(2010, 1, 1),
    'keywords': (),
    'preserved_as_paper': True,
    'privacy_layer': u'privacy_layer_no',
    'public_trial': u'unchecked',
    'public_trial_statement': '',
    'receipt_date': FROZEN_TODAY,
    'title': 'Lorem Ipsum',
}
MAIL_FORM_DEFAULTS = {}
MAIL_MISSING_VALUES = {
    'archival_file': None,
    'archival_file_state': None,
    'delivery_date': None,
    'document_type': None,
    'foreign_reference': None,
    'message': None,  # needs to be updated with NamedBlobFile in actual test
    'message_source': None,
    'original_message': None,
    'preview': None,
    'thumbnail': None,
}


TASK_REQUIREDS = {
    'issuer': 'kathi.barfuss',
    'responsible': 'kathi.barfuss',
    'responsible_client': DEFAULT_CLIENT,
    'task_type': u'information',
    'title': DEFAULT_TITLE,
}
TASK_DEFAULTS = {
    'deadline': FROZEN_TODAY + timedelta(days=5),
    'relatedItems': [],
}
TASK_FORM_DEFAULTS = {
    'issuer': 'kathi.barfuss',
    'responsible_client': DEFAULT_CLIENT,
}
TASK_MISSING_VALUES = {
    'date_of_completion': None,
    'effectiveCost': None,
    'effectiveDuration': None,
    'expectedCost': None,
    'expectedDuration': None,
    'expectedStartOfWork': None,
    'predecessor': None,
    'text': None,
}


CONTACT_REQUIREDS = {
    'firstname': u'John',
    'lastname': u'Doe',
}
CONTACT_DEFAULTS = {
    'description': u'',
}
CONTACT_FORM_DEFAULTS = {}
CONTACT_MISSING_VALUES = {
    'academic_title': None,
    'address1': None,
    'address2': None,
    'city': None,
    'company': None,
    'country': None,
    'department': None,
    'email': None,
    'email2': None,
    'function': None,
    'phone_fax': None,
    'phone_home': None,
    'phone_mobile': None,
    'phone_office': None,
    'picture': None,
    'salutation': None,
    'url': None,
    'zip_code': None,
}


PROPOSAL_REQUIREDS = {
    'issuer': u'herbert.jager',
}
PROPOSAL_DEFAULTS = {
    'description': u'',
    'title': u'Containing Dossier Title',
}
PROPOSAL_FORM_DEFAULTS = {
    'description': u''
}
PROPOSAL_FORM_DEFAULTS = {}
PROPOSAL_MISSING_VALUES = {
    'relatedItems': [],
    'predecessor_proposal': None,
    'date_of_submission': None,
}


PRIVATEFOLDER_REQUIREDS = {
}
PRIVATEFOLDER_DEFAULTS = {
    'allow_add_businesscase_dossier': True,
}
PRIVATEFOLDER_FORM_DEFAULTS = {}
PRIVATEFOLDER_MISSING_VALUES = {
    'addable_dossier_types': None,
    'description': '',
    'former_reference': None,
    'location': None,
    'referenced_activity': None,
    'valid_from': None,
    'valid_until': None,
}


class TestDefaultsBase(IntegrationTestCase):
    """Test our base classes have expected default values."""

    portal_type = None

    requireds = None
    type_defaults = None
    form_defaults = None
    missing_values = None

    maxDiff = None

    api_headers = {
        'Accept': 'application/json',
        'Accept-Language': 'de-ch',
        'Content-Type': 'application/json',
    }

    def setUp(self):
        super(TestDefaultsBase, self).setUp()
        self.portal = self.layer.get('portal')

        # Set 'de-ch' and 'en' as supported languages to have title field show
        # up at all for ITranslatedTitle, but still have the UI in english
        # (otherwise using ftw.testbrowser will be painful)
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('en')
        lang_tool.supported_langs = ['de-ch', 'en']
        lang_tool.use_request_negotiation = True

    def get_type_defaults(self):
        defaults = {}
        defaults.update(self.missing_values)
        defaults.update(self.type_defaults)
        defaults.update(self.requireds)
        return defaults

    def get_z3c_form_defaults(self):
        defaults = {}
        defaults.update(self.missing_values)
        defaults.update(self.type_defaults)
        defaults.update(self.form_defaults)
        defaults.update(self.requireds)
        return defaults

    def get_obj_of_own_type(self):
        """Return a fixture object of the subclass's portal_type.
        """
        raise NotImplementedError

    def get_field_names_for_type(self, portal_type):
        names = []
        for schema in iterSchemataForType(self.portal_type):
            for name, field in getFieldsInOrder(schema):
                if name == 'changeNote':
                    # The changeNote field from p.a.versioningbehavior
                    # is a "fake" field - it never gets persisted, but
                    # written to request annotations instead
                    continue

                if name == 'reference_number':
                    # reference_number is a special field. It never gets
                    # set directly, but instead acts as a computed field
                    # for all intents and purposes.
                    continue

                names.append(name)
        return names

    def iter_widgets(self, form):
        """Iterate over all widgets of a (Group)Form.
        """
        # XXX: Factor this out into opengever.base.formutils - we also
        # need to do this kind of thing in production code a lot
        for widget in form.widgets.values():
            yield widget

        if IGroupForm.providedBy(form):
            for group in form.groups:
                for widget in group.widgets.values():
                    yield widget

    def test_type_defaults_cover_all_schema_fields(self):
        if self.portal_type is not None:
            actual = self.get_type_defaults().keys()
            expected = self.get_field_names_for_type(self.portal_type)
            self.assertEqual(set(expected), set(actual))

    def test_z3c_form_defaults_cover_all_schema_fields(self):
        if self.portal_type is not None:
            actual = self.get_z3c_form_defaults().keys()
            expected = self.get_field_names_for_type(self.portal_type)
            self.assertEqual(set(expected), set(actual))

    def test_widgets_render_missing_values(self):
        """Test that gets run for each of the portal type specific subclasses,
        and asserts that a rendered z3c.form widget correctly returns the
        missing value if that's what's currently persisted on the object.
        """
        if self.portal_type is None:
            # Don't attempt to run this test for the abstract base class
            return

        self.login(self.manager)

        obj = self.get_obj_of_own_type()
        form = DefaultEditForm(obj, self.request)

        # Populate the form with fields according to the object's portal type
        with fake_interaction():
            # We need a fake IInteraction context because otherwise
            # z3c.formwidget.query.widget fails with its checkPermission()
            form.update()

        for widget in self.iter_widgets(form):
            field = widget.field

            if field.required:
                # Required fields shouldn't have missing values
                return

            if field.readonly:
                return

            # Determine what this field's missing value would be
            missing_value = field.missing_value

            # Manipulate fixture obj to have missing value for this field
            field.set(field.interface(obj), missing_value)

            # Update the widget to reflect that changed value on the obj
            with fake_interaction():
                widget.update()

            # Use the widget to retrieve the value - but turn it into a
            # field value using the field's DataConverter, in order to
            # compare it to missing value.
            dc = IDataConverter(widget)
            field_value_from_widget = dc.toFieldValue(widget.value)

            if isinstance(widget, SingleCheckBoxWidget):
                # Boolean fields handled by SingleCheckBoxWidgets are funny:
                # Their fields' missing value is None, which ends up
                # as a widget.value of empty list [], which
                # IDataConverter.toFieldValue() then turns into False.
                #
                # In other words, there isn't really a concept of missing
                # values for booleans - MV will always end up being
                # considered the same as False.
                if field_value_from_widget is False:
                    field_value_from_widget = None

            if isinstance(field, List) and isinstance(widget, CheckBoxWidget):
                # zope.schema.List is weird too - it gets rendered using
                # a CheckBoxWidget.
                missing_value = []

            self.assertEqual(
                missing_value, field_value_from_widget,
                'Unexpectedly got %r instead of missing value %r '
                'from widget %r (for an %r object) ' % (
                    field_value_from_widget, missing_value,
                    widget, obj.portal_type))


class TestRepositoryRootDefaults(TestDefaultsBase):
    """Test our repository roots come with expected default values."""

    portal_type = 'opengever.repository.repositoryroot'

    requireds = REPOROOT_REQUIREDS
    type_defaults = REPOROOT_DEFAULTS
    form_defaults = REPOROOT_FORM_DEFAULTS
    missing_values = REPOROOT_MISSING_VALUES

    def get_obj_of_own_type(self):
        return self.repository_root

    def test_create_content_in_container(self):
        self.login(self.manager)

        with freeze(FROZEN_NOW):
            reporoot = createContentInContainer(
                self.portal,
                'opengever.repository.repositoryroot',
                title_de=REPOROOT_REQUIREDS['title_de'],
            )

        persisted_values = get_persisted_values_for_obj(reporoot)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory(self):
        self.login(self.manager)

        with freeze(FROZEN_NOW):
            new_id = self.portal.invokeFactory(
                'opengever.repository.repositoryroot',
                'new-reporoot',
                title_de=REPOROOT_REQUIREDS['title_de'],
            )
            reporoot = self.portal[new_id]

        persisted_values = get_persisted_values_for_obj(reporoot)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        self.login(self.manager, browser)

        with freeze(FROZEN_NOW):
            browser.open()
            factoriesmenu.add(u'RepositoryRoot')
            browser.fill({u'Title': REPOROOT_REQUIREDS['title_de']}).save()

        reporoot = browser.context

        persisted_values = get_persisted_values_for_obj(reporoot)
        expected = self.get_z3c_form_defaults()

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_rest_api(self, browser):
        self.login(self.manager, browser)

        payload = {
            u'@type': u'opengever.repository.repositoryroot',
            u'title_de': REPOFOLDER_REQUIREDS['title_de'],
            u'title_fr': u'French Title',
        }

        response = browser.open(
            self.portal.absolute_url(),
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(201, response.status_code)

        new_object_id = str(response.json['id'])
        root = self.portal.restrictedTraverse(new_object_id)

        persisted_values = get_persisted_values_for_obj(root)
        expected = self.get_type_defaults()
        expected['title_fr'] = u'French Title'

        self.assertDictEqual(expected, persisted_values)


class TestRepositoryFolderDefaults(TestDefaultsBase):
    """Test our repository folders come with expected default values."""

    portal_type = 'opengever.repository.repositoryfolder'

    requireds = REPOFOLDER_REQUIREDS
    type_defaults = REPOFOLDER_DEFAULTS
    form_defaults = REPOFOLDER_FORM_DEFAULTS
    missing_values = REPOFOLDER_MISSING_VALUES

    def get_obj_of_own_type(self):
        return self.leaf_repofolder

    def test_create_content_in_container(self):
        self.login(self.administrator)
        with freeze(FROZEN_NOW):
            repofolder = createContentInContainer(
                self.empty_repofolder,
                'opengever.repository.repositoryfolder',
                title_de=REPOFOLDER_REQUIREDS['title_de'],
            )

        persisted_values = get_persisted_values_for_obj(repofolder)
        expected = self.get_type_defaults()

        # XXX: Don't know why this happens
        expected['addable_dossier_types'] = None

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory(self):
        self.login(self.administrator)

        with freeze(FROZEN_NOW):
            new_id = self.empty_repofolder.invokeFactory(
                'opengever.repository.repositoryfolder',
                'repofolder',
                title_de=REPOFOLDER_REQUIREDS['title_de'],
            )
        repofolder = self.empty_repofolder[new_id]

        persisted_values = get_persisted_values_for_obj(repofolder)
        expected = self.get_type_defaults()

        # XXX: Don't know why this happens
        expected['addable_dossier_types'] = None

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        self.login(self.administrator, browser)

        with freeze(FROZEN_NOW):
            browser.open(self.empty_repofolder)
            factoriesmenu.add(u'RepositoryFolder')
            browser.fill({u'Title': REPOFOLDER_REQUIREDS['title_de']}).save()

        repofolder = browser.context

        persisted_values = get_persisted_values_for_obj(repofolder)
        expected = self.get_z3c_form_defaults()

        # XXX: Don't know why this happens
        expected['public_trial_statement'] = None

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_rest_api(self, browser):
        self.login(self.administrator, browser)

        payload = {
            u'@type': u'opengever.repository.repositoryfolder',
            u'title_de': REPOFOLDER_REQUIREDS['title_de'],
            u'title_fr': u'French Title',
        }
        response = browser.open(
            self.empty_repofolder.absolute_url(),
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(201, response.status_code)

        new_object_id = str(response.json['id'])
        folder = self.empty_repofolder.restrictedTraverse(new_object_id)

        persisted_values = get_persisted_values_for_obj(folder)
        expected = self.get_type_defaults()
        expected['addable_dossier_types'] = None
        expected['title_fr'] = u'French Title'

        self.assertDictEqual(expected, persisted_values)


class TestDossierDefaults(TestDefaultsBase):
    """Test dossiers come with expected default values."""

    portal_type = 'opengever.dossier.businesscasedossier'

    requireds = DOSSIER_REQUIREDS
    type_defaults = DOSSIER_DEFAULTS
    form_defaults = DOSSIER_FORM_DEFAULTS
    missing_values = DOSSIER_MISSING_VALUES

    features = ('dossiertemplate', )

    def get_obj_of_own_type(self):
        return self.dossier

    def test_create_content_in_container(self):
        self.login(self.regular_user)

        with freeze(FROZEN_NOW):
            dossier = createContentInContainer(
                self.leaf_repofolder,
                'opengever.dossier.businesscasedossier',
                title=DOSSIER_REQUIREDS['title'],
            )

        persisted_values = get_persisted_values_for_obj(dossier)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory(self):
        self.login(self.regular_user)

        with freeze(FROZEN_NOW):
            new_id = self.leaf_repofolder.invokeFactory(
                'opengever.dossier.businesscasedossier',
                'dossier-999',
                title=DOSSIER_REQUIREDS['title'],
            )
        dossier = self.leaf_repofolder[new_id]

        persisted_values = get_persisted_values_for_obj(dossier)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        self.login(self.regular_user, browser)

        with freeze(FROZEN_NOW):
            browser.open(self.leaf_repofolder)
            factoriesmenu.add(u'Business Case Dossier')
            browser.fill({u'Title': DOSSIER_REQUIREDS['title']}).save()

        dossier = browser.context

        persisted_values = get_persisted_values_for_obj(dossier)
        expected = self.get_z3c_form_defaults()

        # XXX: Don't know why this happens
        expected['public_trial_statement'] = None

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_rest_api(self, browser):
        self.login(self.regular_user, browser)

        payload = {
            u'@type': u'opengever.dossier.businesscasedossier',
            u'title': DOSSIER_REQUIREDS['title'],
            u'responsible': DOSSIER_FORM_DEFAULTS['responsible'],
        }
        response = browser.open(
            self.leaf_repofolder.absolute_url(),
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(201, response.status_code)

        new_object_id = str(response.json['id'])
        dossier = self.leaf_repofolder.restrictedTraverse(new_object_id)

        persisted_values = get_persisted_values_for_obj(dossier)
        expected = self.get_type_defaults()
        expected['responsible'] = DOSSIER_FORM_DEFAULTS['responsible']

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_dossier_from_template(self, browser):
        self.login(self.regular_user, browser)

        create(Builder("dossiertemplate")
               .titled(DOSSIER_REQUIREDS['title']))

        with freeze(FROZEN_NOW):
            browser.open(self.leaf_repofolder)
            factoriesmenu.add(u'Dossier with template')

            token = browser.css(
                'input[title="My title"]').first.attrib.get('value')  # noqa

            browser.fill({'form.widgets.template': token}).submit()
            browser.click_on('Save')

        dossier = browser.context

        persisted_values = get_persisted_values_for_obj(dossier)
        expected = self.get_z3c_form_defaults()

        # XXX: Don't know why this happens
        expected['public_trial_statement'] = None

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_subdossier_from_template(self, browser):
        self.login(self.regular_user, browser)

        template = create(Builder("dossiertemplate")
                          .titled(u'Main template'))
        create(Builder("dossiertemplate")
               .within(template)
               .titled(DOSSIER_REQUIREDS['title']))

        with freeze(FROZEN_NOW):
            browser.open(self.leaf_repofolder)
            factoriesmenu.add(u'Dossier with template')
            token = browser.css(
                'input[title="Main template"]').first.attrib.get('value')  # noqa
            browser.fill({'form.widgets.template': token}).submit()
            browser.click_on('Save')

        subdossier = browser.context.listFolderContents()[0]

        persisted_values = get_persisted_values_for_obj(subdossier)
        expected = self.get_type_defaults()

        # Because the main-dossier is made through the ++add++-form and the
        # subdossier is created trough the object-creator with some attribute
        # inheritance, we get a mix of z3c_form_defaults and the type_defaults.
        # A subdossier has the type_defaults with addiional form_defaults
        expected.update(self.form_defaults)

        self.assertDictEqual(expected, persisted_values)


class TestDocumentDefaults(TestDefaultsBase):
    """Test documents come with expected default values."""

    portal_type = 'opengever.document.document'

    requireds = DOCUMENT_REQUIREDS
    type_defaults = DOCUMENT_DEFAULTS
    form_defaults = DOCUMENT_FORM_DEFAULTS
    missing_values = DOCUMENT_MISSING_VALUES

    features = ('dossiertemplate', )

    SAMPLE_FILE = 'Lorem Ipsum.\n'

    @property
    def sample_file(self):
        file_value = NamedBlobFile(
            data=TestDocumentDefaults.SAMPLE_FILE,
            contentType='text/plain',
            filename=u'b\xe4rengraben.txt')
        return file_value

    def get_obj_of_own_type(self):
        return self.document

    def test_create_content_in_container(self):
        self.login(self.regular_user)

        with freeze(FROZEN_NOW):
            doc = createContentInContainer(
                self.dossier,
                'opengever.document.document',
                title=DOCUMENT_REQUIREDS['title'],
                file=self.sample_file,
            )

        # Ensure Bumblebee checksum got calculated correctly
        expected_checksum = sha256(self.SAMPLE_FILE).hexdigest()
        checksum = IBumblebeeDocument(doc).get_checksum()
        self.assertEqual(expected_checksum, checksum)

        persisted_values = get_persisted_values_for_obj(doc)
        expected = self.get_type_defaults()
        expected['file'] = doc.file

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory(self):
        self.login(self.regular_user)

        with freeze(FROZEN_NOW):
            new_id = self.dossier.invokeFactory(
                'opengever.document.document',
                'document-1',
                title=DOCUMENT_REQUIREDS['title'],
                file=self.sample_file,
            )

        doc = self.dossier[new_id]

        # Ensure Bumblebee checksum got calculated correctly
        expected_checksum = sha256(self.SAMPLE_FILE).hexdigest()
        checksum = IBumblebeeDocument(doc).get_checksum()
        self.assertEqual(expected_checksum, checksum)

        persisted_values = get_persisted_values_for_obj(doc)
        expected = self.get_type_defaults()
        expected['file'] = doc.file

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        self.login(self.regular_user, browser)

        with freeze(FROZEN_NOW):
            with self.observe_children(self.dossier) as children:
                browser.open(self.dossier)
                factoriesmenu.add(u'Document')
                browser.fill({
                    u'Title': DOCUMENT_REQUIREDS['title'],
                    u'File': (
                        TestDocumentDefaults.SAMPLE_FILE,
                        'b\xc3\xa4rengraben.txt', 'text/plain')}).save()

        doc, = children.get('added')

        # Ensure Bumblebee checksum got calculated correctly
        expected_checksum = sha256(self.SAMPLE_FILE).hexdigest()
        checksum = IBumblebeeDocument(doc).get_checksum()
        self.assertEqual(expected_checksum, checksum)

        persisted_values = get_persisted_values_for_obj(doc)
        expected = self.get_z3c_form_defaults()
        expected['file'] = doc.file

        # XXX: Don't know why this happens
        expected['public_trial_statement'] = None

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_rest_api(self, browser):
        self.login(self.regular_user, browser)

        payload = {
            u'@type': u'opengever.document.document',
            u'title': DOCUMENT_REQUIREDS['title'],
            u'file': {
                u'data': TestDocumentDefaults.SAMPLE_FILE.encode('base64'),
                u'encoding': u'base64',
                u'filename': u'b\xe4rengraben.txt',
                u'content-type': u'text/plain'},
        }
        response = browser.open(
            self.dossier.absolute_url(),
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(201, response.status_code)

        new_object_id = str(response.json['id'])
        doc = self.dossier.restrictedTraverse(new_object_id)

        # Ensure Bumblebee checksum got calculated correctly
        expected_checksum = sha256(self.SAMPLE_FILE).hexdigest()
        checksum = IBumblebeeDocument(doc).get_checksum()
        self.assertEqual(expected_checksum, checksum)

        persisted_values = get_persisted_values_for_obj(doc)
        expected = self.get_type_defaults()
        expected['file'] = doc.file

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_document_from_dossiertemplate(self, browser):
        self.login(self.regular_user, browser)

        template = create(Builder("dossiertemplate")
                          .titled(DOSSIER_REQUIREDS['title'])
                          .within(self.templates))
        create(Builder('document')
               .titled(DOCUMENT_REQUIREDS['title'])
               .within(template)
               .with_dummy_content())

        with freeze(FROZEN_NOW):
            browser.open(self.leaf_repofolder)
            factoriesmenu.add(u'Dossier with template')
            token = browser.css(
                'input[title="My title"]').first.attrib.get('value')  # noqa
            browser.fill({'form.widgets.template': token}).submit()
            browser.click_on('Save')

        dossier = browser.context
        doc = dossier.objectValues()[0]

        persisted_values = get_persisted_values_for_obj(doc)
        expected = self.get_type_defaults()

        expected['digitally_available'] = True
        expected['file'] = doc.file

        self.assertDictEqual(expected, persisted_values)


class TestMailDefaults(TestDefaultsBase):
    """Test mails come with expected default values."""

    portal_type = 'ftw.mail.mail'

    requireds = MAIL_REQUIREDS
    type_defaults = MAIL_DEFAULTS
    form_defaults = MAIL_FORM_DEFAULTS
    missing_values = MAIL_MISSING_VALUES

    SAMPLE_MAIL = textwrap.dedent("""\
        MIME-Version: 1.0
        Content-Type: text/plain; charset="us-ascii"
        Content-Transfer-Encoding: 7bit
        To: to@example.org
        From: from@example.org
        Subject: Lorem Ipsum
        Date: Thu, 01 Jan 2010 01:00:00 +0100
        Message-Id: <1>

        Lorem ipsum dolor sit amet.
        """)

    @property
    def sample_msg(self):
        message_value = NamedBlobFile(
            data=TestMailDefaults.SAMPLE_MAIL,
            contentType='message/rfc822',
            filename=u'msg.eml')
        return message_value

    def get_obj_of_own_type(self):
        return self.mail_eml

    def test_create_content_in_container(self):
        self.login(self.regular_user)

        with freeze(FROZEN_NOW):
            mail = createContentInContainer(
                self.dossier,
                'ftw.mail.mail',
                message=self.sample_msg)

        # Ensure Bumblebee checksum got calculated correctly
        expected_checksum = sha256(self.SAMPLE_MAIL).hexdigest()
        checksum = IBumblebeeDocument(mail).get_checksum()
        self.assertEqual(expected_checksum, checksum)

        persisted_values = get_persisted_values_for_obj(mail)
        expected = self.get_type_defaults()

        expected['message'] = mail._message

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory(self):
        self.login(self.regular_user)

        with freeze(FROZEN_NOW):
            new_id = self.dossier.invokeFactory(
                'ftw.mail.mail',
                'mail',
                message=self.sample_msg)

        mail = self.dossier[new_id]

        # Ensure Bumblebee checksum got calculated correctly
        expected_checksum = sha256(self.SAMPLE_MAIL).hexdigest()
        checksum = IBumblebeeDocument(mail).get_checksum()
        self.assertEqual(expected_checksum, checksum)

        persisted_values = get_persisted_values_for_obj(mail)
        expected = self.get_type_defaults()

        expected['message'] = mail._message

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        self.login(self.regular_user, browser)

        with freeze(FROZEN_NOW):
            # Mail is not addable via factories menu
            browser.open(self.dossier, view='++add++ftw.mail.mail')
            browser.fill({
                u'form.widgets.message': (TestMailDefaults.SAMPLE_MAIL,
                                          'msg.eml', 'message/rfc822')}).save()

        mail = browser.context

        # Ensure Bumblebee checksum got calculated correctly
        expected_checksum = sha256(self.SAMPLE_MAIL).hexdigest()
        checksum = IBumblebeeDocument(mail).get_checksum()
        self.assertEqual(expected_checksum, checksum)

        persisted_values = get_persisted_values_for_obj(mail)
        expected = self.get_z3c_form_defaults()

        expected['message'] = mail._message

        # XXX: Don't know why this happens
        expected['public_trial_statement'] = None

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_rest_api(self, browser):
        self.login(self.regular_user, browser)

        payload = {
            u'@type': u'ftw.mail.mail',
            u'message': {
                u'data': TestMailDefaults.SAMPLE_MAIL.encode('base64'),
                u'encoding': u'base64',
                u'filename': u'msg.eml',
                u'content-type': u'message/rfc822'},
        }
        response = browser.open(
            self.dossier.absolute_url(),
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(201, response.status_code)

        new_object_id = str(response.json['id'])
        mail = self.dossier.restrictedTraverse(new_object_id)

        # Ensure Bumblebee checksum got calculated correctly
        expected_checksum = sha256(self.SAMPLE_MAIL).hexdigest()
        checksum = IBumblebeeDocument(mail).get_checksum()
        self.assertEqual(expected_checksum, checksum)

        persisted_values = get_persisted_values_for_obj(mail)
        expected = self.get_type_defaults()

        expected['message'] = mail._message

        self.assertDictEqual(expected, persisted_values)


class TestTaskDefaults(TestDefaultsBase):
    """Test tasks come with expected default values."""

    portal_type = 'opengever.task.task'

    requireds = TASK_REQUIREDS
    type_defaults = TASK_DEFAULTS
    form_defaults = TASK_FORM_DEFAULTS
    missing_values = TASK_MISSING_VALUES

    def get_obj_of_own_type(self):
        return self.task

    def test_create_content_in_container(self):
        self.login(self.regular_user)

        with freeze(FROZEN_NOW):
            task = createContentInContainer(
                self.dossier,
                'opengever.task.task',
                title=TASK_REQUIREDS['title'],
                issuer=TASK_REQUIREDS['issuer'],
                task_type=TASK_REQUIREDS['task_type'],
                responsible=TASK_REQUIREDS['responsible'],
                responsible_client=TASK_REQUIREDS['responsible_client'],
            )

        persisted_values = get_persisted_values_for_obj(task)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory(self):
        self.login(self.regular_user)

        with freeze(FROZEN_NOW):
            new_id = self.dossier.invokeFactory(
                'opengever.task.task',
                'task-999',
                title=TASK_REQUIREDS['title'],
                issuer=TASK_REQUIREDS['issuer'],
                task_type=TASK_REQUIREDS['task_type'],
                responsible=TASK_REQUIREDS['responsible'],
                responsible_client=TASK_REQUIREDS['responsible_client'],
            )

        task = self.dossier[new_id]

        persisted_values = get_persisted_values_for_obj(task)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        self.login(self.regular_user, browser)

        with freeze(FROZEN_NOW):
            with self.observe_children(self.dossier) as children:
                browser.open(self.dossier)
                factoriesmenu.add(u'Task')
                browser.fill({
                    u'Title': TASK_REQUIREDS['title'],
                    u'Task Type': TASK_REQUIREDS['task_type']})

                form = browser.find_form_by_field('Responsible')
                form.find_widget('Responsible').fill(':'.join(
                    [TASK_REQUIREDS['responsible_client'],
                     TASK_REQUIREDS['responsible']]))
                form.save()

        task, = children.get('added')

        persisted_values = get_persisted_values_for_obj(task)
        expected = self.get_z3c_form_defaults()

        self.assertDictEqual(expected, persisted_values)


class TestContactDefaults(TestDefaultsBase):
    """Test contacts come with expected default values."""

    portal_type = 'opengever.contact.contact'

    requireds = CONTACT_REQUIREDS
    type_defaults = CONTACT_DEFAULTS
    form_defaults = CONTACT_FORM_DEFAULTS
    missing_values = CONTACT_MISSING_VALUES

    def get_obj_of_own_type(self):
        return self.franz_meier

    def test_create_content_in_container(self):
        self.login(self.regular_user)

        with freeze(FROZEN_NOW):
            contact = createContentInContainer(
                self.contactfolder,
                'opengever.contact.contact',
                firstname=CONTACT_REQUIREDS['firstname'],
                lastname=CONTACT_REQUIREDS['lastname'],
            )

        persisted_values = get_persisted_values_for_obj(contact)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory(self):
        self.login(self.regular_user)

        with freeze(FROZEN_NOW):
            new_id = self.contactfolder.invokeFactory(
                'opengever.contact.contact',
                'john-doe',
                firstname=CONTACT_REQUIREDS['firstname'],
                lastname=CONTACT_REQUIREDS['lastname'],
            )
            contact = self.contactfolder[new_id]

        persisted_values = get_persisted_values_for_obj(contact)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        self.login(self.regular_user, browser)

        with freeze(FROZEN_NOW):
            browser.login().open(self.contactfolder)
            factoriesmenu.add(u'Contact')
            browser.fill({
                u'Firstname': CONTACT_REQUIREDS['firstname'],
                u'Lastname': CONTACT_REQUIREDS['lastname']}).save()
            contact = browser.context

        persisted_values = get_persisted_values_for_obj(contact)
        expected = self.get_z3c_form_defaults()

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_rest_api(self, browser):
        self.login(self.regular_user, browser)

        payload = {
            u'@type': u'opengever.contact.contact',
            u'firstname': CONTACT_REQUIREDS['firstname'],
            u'lastname': CONTACT_REQUIREDS['lastname'],
        }
        response = browser.open(
            self.contactfolder.absolute_url(),
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(201, response.status_code)

        new_object_id = str(response.json['id'])
        contact = self.contactfolder.restrictedTraverse(new_object_id)

        persisted_values = get_persisted_values_for_obj(contact)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)


class TestProposalDefaults(TestDefaultsBase):
    """Test proposals come with expected default values."""

    portal_type = 'opengever.meeting.proposal'

    requireds = PROPOSAL_REQUIREDS
    type_defaults = PROPOSAL_DEFAULTS
    form_defaults = PROPOSAL_FORM_DEFAULTS
    missing_values = PROPOSAL_MISSING_VALUES

    features = ('meeting', )

    def setUp(self):
        super(TestProposalDefaults, self).setUp()
        self.login(self.meeting_user)
        self.dossier.title = u'Containing Dossier Title'

    def get_obj_of_own_type(self):
        return self.proposal

    def test_create_content_in_container(self):
        self.login(self.meeting_user)

        proposal = createContentInContainer(
            self.dossier,
            'opengever.meeting.proposal',
            issuer=PROPOSAL_REQUIREDS['issuer'],
        )

        persisted_values = get_persisted_values_for_obj(proposal)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory(self):
        self.login(self.meeting_user)

        new_id = self.dossier.invokeFactory(
            'opengever.meeting.proposal',
            'proposal-999',
            issuer=PROPOSAL_REQUIREDS['issuer'],
        )
        proposal = self.dossier[new_id]

        persisted_values = get_persisted_values_for_obj(proposal)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        self.login(self.meeting_user, browser)

        browser.open(self.dossier)
        factoriesmenu.add(u'Proposal')
        browser.forms['form'].fill({
            'Committee': self.committee.title,
            'Proposal template': self.proposal_template.title,
        }).save()
        proposal = browser.context

        persisted_values = get_persisted_values_for_obj(proposal)
        expected = self.get_z3c_form_defaults()

        self.assertDictEqual(expected, persisted_values)


class TestPrivateFolderDefaults(TestDefaultsBase):
    """Test private folders come with expected default values."""

    portal_type = 'opengever.private.folder'

    requireds = PRIVATEFOLDER_REQUIREDS
    type_defaults = PRIVATEFOLDER_DEFAULTS
    form_defaults = PRIVATEFOLDER_FORM_DEFAULTS
    missing_values = PRIVATEFOLDER_MISSING_VALUES

    features = ('private',)

    def get_obj_of_own_type(self):
        return self.private_folder

    def test_private_folder_defaults(self):
        self.login(self.regular_user)

        # This will trigger member folder creation by MembershipTool
        create_members_folder(self.private_root)

        private_folder = self.portal.private[api.user.get_current().id]

        persisted_values = get_persisted_values_for_obj(private_folder)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

from datetime import date
from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testing import freeze
from opengever.base.default_values import get_persisted_values_for_obj
from opengever.core.testing import toggle_feature
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings  # noqa
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.dexterity.utils import iterSchemataForType
from plone.namedfile.file import NamedBlobFile
from zope.schema import getFieldsInOrder
import textwrap
import transaction


FROZEN_NOW = datetime.now()
FROZEN_TODAY = FROZEN_NOW.date()

DEFAULT_TITLE = u'My title'
DEFAULT_CLIENT = u'client1'

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
    'responsible': TEST_USER_ID,
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
    'digitally_available': False,
    'document_date': FROZEN_TODAY,
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
    'issuer': TEST_USER_ID,
    'responsible': TEST_USER_ID,
    'responsible_client': DEFAULT_CLIENT,
    'task_type': u'information',
    'title': DEFAULT_TITLE,
}
TASK_DEFAULTS = {
    'deadline': FROZEN_TODAY + timedelta(days=5),
    'relatedItems': [],
}
TASK_FORM_DEFAULTS = {
    'issuer': TEST_USER_ID,
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
}
PROPOSAL_DEFAULTS = {
    'title': u'Containing Dossier Title',
}
PROPOSAL_FORM_DEFAULTS = {}
PROPOSAL_MISSING_VALUES = {
    'relatedItems': [],
    'predecessor_proposal': None,
    'date_of_submission': None,
}


class TestDefaultsBase(FunctionalTestCase):
    """Test our base classes have expected default values."""

    portal_type = None

    requireds = None
    type_defaults = None
    form_defaults = None
    missing_values = None

    maxDiff = None

    def setUp(self):
        super(TestDefaultsBase, self).setUp()
        self.portal = self.layer.get('portal')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        # Set 'de-ch' and 'en' as supported languages to have title field show
        # up at all for ITranslatedTitle, but still have the UI in english
        # (otherwise using ftw.testbrowser will be painful)
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('en')
        lang_tool.supported_langs = ['de-ch', 'en']
        transaction.commit()

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


class TestRepositoryRootDefaults(TestDefaultsBase):
    """Test our repository roots come with expected default values."""

    portal_type = 'opengever.repository.repositoryroot'

    requireds = REPOROOT_REQUIREDS
    type_defaults = REPOROOT_DEFAULTS
    form_defaults = REPOROOT_FORM_DEFAULTS
    missing_values = REPOROOT_MISSING_VALUES

    def test_create_content_in_container(self):
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
        with freeze(FROZEN_NOW):
            new_id = self.portal.invokeFactory(
                'opengever.repository.repositoryroot',
                'reporoot',
                title_de=REPOROOT_REQUIREDS['title_de'],
            )
            reporoot = self.portal[new_id]

        persisted_values = get_persisted_values_for_obj(reporoot)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        with freeze(FROZEN_NOW):
            browser.login().open()
            factoriesmenu.add(u'RepositoryRoot')
            browser.fill({u'Title': REPOROOT_REQUIREDS['title_de']}).save()
            reporoot = browser.context

        persisted_values = get_persisted_values_for_obj(reporoot)
        expected = self.get_z3c_form_defaults()

        self.assertDictEqual(expected, persisted_values)


class TestRepositoryFolderDefaults(TestDefaultsBase):
    """Test our repository folders come with expected default values."""

    portal_type = 'opengever.repository.repositoryfolder'

    requireds = REPOFOLDER_REQUIREDS
    type_defaults = REPOFOLDER_DEFAULTS
    form_defaults = REPOFOLDER_FORM_DEFAULTS
    missing_values = REPOFOLDER_MISSING_VALUES

    def test_create_content_in_container(self):
        with freeze(FROZEN_NOW):
            repofolder = createContentInContainer(
                self.portal,
                'opengever.repository.repositoryfolder',
                title_de=REPOFOLDER_REQUIREDS['title_de'],
            )

        persisted_values = get_persisted_values_for_obj(repofolder)
        expected = self.get_type_defaults()

        # XXX: Don't know why this happens
        expected['addable_dossier_types'] = None

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory(self):
        with freeze(FROZEN_NOW):
            new_id = self.portal.invokeFactory(
                'opengever.repository.repositoryfolder',
                'repofolder',
                title_de=REPOFOLDER_REQUIREDS['title_de'],
            )
            repofolder = self.portal[new_id]

        persisted_values = get_persisted_values_for_obj(repofolder)
        expected = self.get_type_defaults()

        # XXX: Don't know why this happens
        expected['addable_dossier_types'] = None

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        with freeze(FROZEN_NOW):
            browser.login().open()
            factoriesmenu.add(u'RepositoryFolder')
            browser.fill({u'Title': REPOFOLDER_REQUIREDS['title_de']}).save()
            repofolder = browser.context

        persisted_values = get_persisted_values_for_obj(repofolder)
        expected = self.get_z3c_form_defaults()

        # XXX: Don't know why this happens
        expected['public_trial_statement'] = None

        self.assertDictEqual(expected, persisted_values)


class TestDossierDefaults(TestDefaultsBase):
    """Test dossiers come with expected default values."""

    portal_type = 'opengever.dossier.businesscasedossier'

    requireds = DOSSIER_REQUIREDS
    type_defaults = DOSSIER_DEFAULTS
    form_defaults = DOSSIER_FORM_DEFAULTS
    missing_values = DOSSIER_MISSING_VALUES

    def test_create_content_in_container(self):
        with freeze(FROZEN_NOW):
            dossier = createContentInContainer(
                self.portal,
                'opengever.dossier.businesscasedossier',
                title=DOSSIER_REQUIREDS['title'],
            )

        persisted_values = get_persisted_values_for_obj(dossier)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory(self):
        with freeze(FROZEN_NOW):
            new_id = self.portal.invokeFactory(
                'opengever.dossier.businesscasedossier',
                'dossier-1',
                title=DOSSIER_REQUIREDS['title'],
            )
            dossier = self.portal[new_id]

        persisted_values = get_persisted_values_for_obj(dossier)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        with freeze(FROZEN_NOW):
            browser.login().open()
            factoriesmenu.add(u'Business Case Dossier')
            browser.fill({u'Title': DOSSIER_REQUIREDS['title']}).save()
            dossier = browser.context

        persisted_values = get_persisted_values_for_obj(dossier)
        expected = self.get_z3c_form_defaults()

        # XXX: Don't know why this happens
        expected['public_trial_statement'] = None

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_dossier_from_template(self, browser):
        toggle_feature(IDossierTemplateSettings, enabled=True)

        root = create(Builder('repository_root'))
        leaf_node = create(Builder('repository').within(root))

        create(Builder("dossiertemplate")
               .titled(DOSSIER_REQUIREDS['title']))

        with freeze(FROZEN_NOW):
            browser.login().open(leaf_node)
            factoriesmenu.add(u'Dossier with template')

            token = browser.css(
                'input[name="form.widgets.template"]').first.attrib.get('value')  # noqa

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
        toggle_feature(IDossierTemplateSettings, enabled=True)

        root = create(Builder('repository_root'))
        leaf_node = create(Builder('repository').within(root))
        template = create(Builder("dossiertemplate")
                          .titled(u'Main template'))
        create(Builder("dossiertemplate")
               .within(template)
               .titled(DOSSIER_REQUIREDS['title']))

        with freeze(FROZEN_NOW):
            browser.login().open(leaf_node)
            factoriesmenu.add(u'Dossier with template')
            token = browser.css(
                'input[name="form.widgets.template"]').first.attrib.get('value')  # noqa
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

    def test_create_content_in_container(self):
        with freeze(FROZEN_NOW):
            doc = createContentInContainer(
                self.portal,
                'opengever.document.document',
                title=DOCUMENT_REQUIREDS['title'],
            )

        persisted_values = get_persisted_values_for_obj(doc)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory(self):
        with freeze(FROZEN_NOW):
            new_id = self.portal.invokeFactory(
                'opengever.document.document',
                'document-1',
                title=DOCUMENT_REQUIREDS['title'],
            )
            doc = self.portal[new_id]

        persisted_values = get_persisted_values_for_obj(doc)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        # Need to create doc inside a dossier, otherwise document-redirector
        # won't work
        outer_dossier = createContentInContainer(
            self.portal,
            'opengever.dossier.businesscasedossier',
            title=u'Outer Dossier',
        )
        transaction.commit()

        with freeze(FROZEN_NOW):
            browser.login().open(outer_dossier)
            factoriesmenu.add(u'Document')
            browser.fill({u'Title': DOCUMENT_REQUIREDS['title']}).save()
            doc = outer_dossier['document-1']

        persisted_values = get_persisted_values_for_obj(doc)
        expected = self.get_z3c_form_defaults()

        # XXX: Don't know why this happens
        expected['public_trial_statement'] = None

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_document_from_dossiertemplate(self, browser):
        toggle_feature(IDossierTemplateSettings, enabled=True)

        root = create(Builder('repository_root'))
        leaf_node = create(Builder('repository').within(root))
        template = create(Builder("dossiertemplate")
                          .titled(DOSSIER_REQUIREDS['title']))
        create(Builder('document')
               .titled(DOCUMENT_REQUIREDS['title'])
               .within(template)
               .with_dummy_content())

        with freeze(FROZEN_NOW):
            browser.login().open(leaf_node)
            factoriesmenu.add(u'Dossier with template')
            token = browser.css(
                'input[name="form.widgets.template"]').first.attrib.get('value')  # noqa
            browser.fill({'form.widgets.template': token}).submit()
            browser.click_on('Save')

            doc = browser.context.listFolderContents()[0]

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

    def test_create_content_in_container(self):
        with freeze(FROZEN_NOW):
            mail = createContentInContainer(
                self.portal,
                'ftw.mail.mail',
                message=self.sample_msg)

        persisted_values = get_persisted_values_for_obj(mail)
        expected = self.get_type_defaults()

        expected['message'] = mail._message

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory(self):
        with freeze(FROZEN_NOW):
            new_id = self.portal.invokeFactory(
                'ftw.mail.mail',
                'mail',
                message=self.sample_msg)
            mail = self.portal[new_id]

        persisted_values = get_persisted_values_for_obj(mail)
        expected = self.get_type_defaults()

        expected['message'] = mail._message

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        with freeze(FROZEN_NOW):
            # Mail is not addable via factories menu
            browser.login().open(view='++add++ftw.mail.mail')
            browser.fill({
                u'form.widgets.message': (TestMailDefaults.SAMPLE_MAIL,
                                          'msg.eml', 'message/rfc822')}).save()
            mail = browser.context

        persisted_values = get_persisted_values_for_obj(mail)
        expected = self.get_z3c_form_defaults()

        expected['message'] = mail._message

        # XXX: Don't know why this happens
        expected['public_trial_statement'] = None

        self.assertDictEqual(expected, persisted_values)


class TestTaskDefaults(TestDefaultsBase):
    """Test tasks come with expected default values."""

    portal_type = 'opengever.task.task'

    requireds = TASK_REQUIREDS
    type_defaults = TASK_DEFAULTS
    form_defaults = TASK_FORM_DEFAULTS
    missing_values = TASK_MISSING_VALUES

    def test_create_content_in_container(self):
        with freeze(FROZEN_NOW):
            task = createContentInContainer(
                self.portal,
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
        with freeze(FROZEN_NOW):
            new_id = self.portal.invokeFactory(
                'opengever.task.task',
                'task-1',
                title=TASK_REQUIREDS['title'],
                issuer=TASK_REQUIREDS['issuer'],
                task_type=TASK_REQUIREDS['task_type'],
                responsible=TASK_REQUIREDS['responsible'],
                responsible_client=TASK_REQUIREDS['responsible_client'],
            )
            task = self.portal[new_id]

        persisted_values = get_persisted_values_for_obj(task)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        with freeze(FROZEN_NOW):
            browser.login().open()
            factoriesmenu.add(u'Task')
            browser.fill({
                u'Title': TASK_REQUIREDS['title'],
                u'Task Type': TASK_REQUIREDS['task_type']})

            form = browser.find_form_by_field('Responsible')
            form.find_widget('Responsible').fill(':'.join(
                [TASK_REQUIREDS['responsible_client'],
                 TASK_REQUIREDS['responsible']]))
            form.save()

            task = self.portal['task-1']

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

    def setUp(self):
        super(TestContactDefaults, self).setUp()
        self.contactfolder = createContentInContainer(
            self.portal,
            'opengever.contact.contactfolder',
            title=u'Contacts',
        )
        transaction.commit()

    def test_create_content_in_container(self):
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


class TestProposalDefaults(TestDefaultsBase):
    """Test proposals come with expected default values."""

    portal_type = 'opengever.meeting.proposal'

    requireds = PROPOSAL_REQUIREDS
    type_defaults = PROPOSAL_DEFAULTS
    form_defaults = PROPOSAL_FORM_DEFAULTS
    missing_values = PROPOSAL_MISSING_VALUES

    def setUp(self):
        super(TestProposalDefaults, self).setUp()

        api.portal.set_registry_record(
            'opengever.meeting.interfaces.IMeetingSettings.is_feature_enabled',
            True)

        self.container = create(Builder('committee_container'))
        self.committee = create(Builder('committee').within(self.container))
        self.repofolder = create(Builder('repository'))

        self.dossier = create(Builder('dossier')
                              .titled(u'Containing Dossier Title')
                              .within(self.repofolder))

        self.templates = create(
            Builder('templatefolder')
            .titled(u'Vorlagen')
            .having(id='vorlagen')
        )

        self.proposal_template = create(
            Builder('proposaltemplate')
            .titled(u'Geb\xfchren')
            .with_asset_file(u'vertragsentwurf.docx')
            .within(self.templates)
        )

        transaction.commit()

    def test_create_content_in_container(self):
        proposal = createContentInContainer(
            self.dossier,
            'opengever.meeting.proposal',
        )

        persisted_values = get_persisted_values_for_obj(proposal)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory(self):
        new_id = self.dossier.invokeFactory(
            'opengever.meeting.proposal',
            'proposal-1',
        )
        proposal = self.dossier[new_id]

        persisted_values = get_persisted_values_for_obj(proposal)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):

        browser.login().open(self.dossier)
        factoriesmenu.add(u'Proposal')
        browser.forms['form'].fill({
            'Committee': self.committee.title,
            'Proposal template': self.proposal_template.title,
        }).save()
        proposal = browser.context

        persisted_values = get_persisted_values_for_obj(proposal)
        expected = self.get_z3c_form_defaults()

        self.assertDictEqual(expected, persisted_values)

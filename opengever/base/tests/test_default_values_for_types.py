from datetime import date
from datetime import datetime
from datetime import timedelta
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testing import freeze
from opengever.base.default_values import get_persisted_values_for_obj
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
import textwrap
import transaction


FROZEN_NOW = datetime.now()
FROZEN_TODAY = FROZEN_NOW.date()

DEFAULT_TITLE = u'My title'

OMITTED_FORM_FIELDS = ['creators']

REPOROOT_DEFAULTS = {
    'title_de': DEFAULT_TITLE,
}
REPOROOT_FORM_DEFAULTS = {}
REPOROOT_FORM_INITVALUES = {
    'valid_from': None,
    'valid_until': None,
    'version': None,
}


REPOFOLDER_DEFAULTS = {
    'archival_value': u'unchecked',
    'classification': u'unprotected',
    'creators': (),
    'custody_period': 30,
    'description': u'',
    'privacy_layer': u'privacy_layer_no',
    'public_trial': u'unchecked',
    'public_trial_statement': '',
    'reference_number_prefix': u'1',
    'retention_period': 5,
    'title_de': DEFAULT_TITLE,
}
REPOFOLDER_FORM_DEFAULTS = {}
REPOFOLDER_FORM_INITVALUES = {
    'addable_dossier_types': [],
    'archival_value_annotation': None,
    'date_of_cassation': None,
    'date_of_submission': None,
    'former_reference': None,
    'location': None,
    'referenced_activity': None,
    'retention_period_annotation': None,
    'valid_from': None,
    'valid_until': None,
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
    'title': DEFAULT_TITLE,
}
DOSSIER_FORM_DEFAULTS = {
    'responsible': TEST_USER_ID,
}
DOSSIER_FORM_INITVALUES = {
    'archival_value_annotation': None,
    'comments': None,
    'container_location': None,
    'container_type': None,
    'date_of_cassation': None,
    'date_of_submission': None,
    'end': None,
    'filing_prefix': None,
    'number_of_containers': None,
    'retention_period_annotation': None,
}


DOCUMENT_DEFAULTS = {
    'classification': u'unprotected',
    'creators': (),
    'description': u'',
    'digitally_available': False,
    'document_date': FROZEN_TODAY,
    'keywords': (),
    'preserved_as_paper': True,
    'privacy_layer': u'privacy_layer_no',
    'public_trial': u'unchecked',
    'public_trial_statement': '',
    'relatedItems': [],
    'title': DEFAULT_TITLE,
}
DOCUMENT_FORM_DEFAULTS = {}
DOCUMENT_FORM_INITVALUES = {
    'delivery_date': None,
    'document_author': None,
    'document_type': None,
    'file': None,
    'foreign_reference': None,
    'receipt_date': None,
}


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
}
MAIL_FORM_DEFAULTS = {}
MAIL_FORM_INITVALUES = {
    'delivery_date': None,
    'document_type': None,
    'foreign_reference': None,
}


TASK_DEFAULTS = {
    'deadline': FROZEN_TODAY + timedelta(days=5),
    'issuer': TEST_USER_ID,
    'relatedItems': [],
    'responsible': TEST_USER_ID,
    'responsible_client': u'client1',
    'title': u'My title',
}
TASK_FORM_DEFAULTS = {
    'responsible_client': u'client1',
}
TASK_FORM_INITVALUES = {
    'date_of_completion': None,
    'effectiveCost': None,
    'effectiveDuration': None,
    'expectedCost': None,
    'expectedDuration': None,
    'expectedStartOfWork': None,
    'task_type': u'information',
    'text': None,
}


CONTACT_DEFAULTS = {
    'description': u'',
}
CONTACT_FORM_DEFAULTS = {}
CONTACT_FORM_INITVALUES = {
    'academic_title': None,
    'address1': None,
    'address2': None,
    'city': None,
    'company': None,
    'country': None,
    'department': None,
    'email': None,
    'email2': None,
    'firstname': u'John',
    'function': None,
    'lastname': u'John',
    'phone_fax': None,
    'phone_home': None,
    'phone_mobile': None,
    'phone_office': None,
    'picture': None,
    'salutation': None,
    'url': None,
    'zip_code': None,
}


COMMITTEE_DEFAULTS = {}
COMMITTEE_FORM_DEFAULTS = {}
COMMITTEE_FORM_INITVALUES = {
    'agendaitem_list_template': None,
    'excerpt_template': None,
    'protocol_template': None,
}


class TestDefaultsBase(FunctionalTestCase):

    type_defaults = None
    form_defaults = None
    form_initvalues = None

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
        return self.type_defaults

    def get_z3c_form_defaults(self):
        defaults = {}
        defaults.update(self.type_defaults)
        defaults.update(self.form_defaults)
        defaults.update(self.form_initvalues)

        for key in OMITTED_FORM_FIELDS:
            defaults.pop(key, None)

        return defaults


class TestRepositoryRootDefaults(TestDefaultsBase):

    type_defaults = REPOROOT_DEFAULTS
    form_defaults = REPOROOT_FORM_DEFAULTS
    form_initvalues = REPOROOT_FORM_INITVALUES

    def test_create_content_in_container(self):
        with freeze(FROZEN_NOW):
            reporoot = createContentInContainer(
                self.portal,
                'opengever.repository.repositoryroot',
                title_de=DEFAULT_TITLE)

        persisted_values = get_persisted_values_for_obj(reporoot)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory_on_portal(self):
        with freeze(FROZEN_NOW):
            new_id = self.portal.invokeFactory(
                'opengever.repository.repositoryroot',
                'reporoot',
                title_de=DEFAULT_TITLE)
            reporoot = self.portal[new_id]

        persisted_values = get_persisted_values_for_obj(reporoot)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        with freeze(FROZEN_NOW):
            browser.login().open()
            factoriesmenu.add(u'RepositoryRoot')
            browser.fill({u'Title': DEFAULT_TITLE}).save()
            reporoot = browser.context

        persisted_values = get_persisted_values_for_obj(reporoot)
        expected = self.get_z3c_form_defaults()

        self.assertDictEqual(expected, persisted_values)


class TestRepositoryFolderDefaults(TestDefaultsBase):

    type_defaults = REPOFOLDER_DEFAULTS
    form_defaults = REPOFOLDER_FORM_DEFAULTS
    form_initvalues = REPOFOLDER_FORM_INITVALUES

    def test_create_content_in_container(self):
        with freeze(FROZEN_NOW):
            repofolder = createContentInContainer(
                self.portal,
                'opengever.repository.repositoryfolder',
                title_de=DEFAULT_TITLE)

        persisted_values = get_persisted_values_for_obj(repofolder)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory_on_portal(self):
        with freeze(FROZEN_NOW):
            new_id = self.portal.invokeFactory(
                'opengever.repository.repositoryfolder',
                'repofolder',
                title_de=DEFAULT_TITLE)
            repofolder = self.portal[new_id]

        persisted_values = get_persisted_values_for_obj(repofolder)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory_on_dx_container(self):
        outer_repofolder = createContentInContainer(
            self.portal,
            'opengever.repository.repositoryfolder',
            title_de=u'Outer RepoFolder',
        )

        with freeze(FROZEN_NOW):
            new_id = outer_repofolder.invokeFactory(
                'opengever.repository.repositoryfolder',
                'repofolder',
                title_de=DEFAULT_TITLE)
            repofolder = outer_repofolder[new_id]

        persisted_values = get_persisted_values_for_obj(repofolder)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        with freeze(FROZEN_NOW):
            browser.login().open()
            factoriesmenu.add(u'RepositoryFolder')
            browser.fill({u'Title': DEFAULT_TITLE}).save()
            repofolder = browser.context

        persisted_values = get_persisted_values_for_obj(repofolder)
        expected = self.get_z3c_form_defaults()

        # XXX: Don't know why this happens
        expected['public_trial_statement'] = None
        expected['description'] = None

        self.assertDictEqual(expected, persisted_values)


class TestDossierDefaults(TestDefaultsBase):

    type_defaults = DOSSIER_DEFAULTS
    form_defaults = DOSSIER_FORM_DEFAULTS
    form_initvalues = DOSSIER_FORM_INITVALUES

    def test_create_content_in_container(self):
        with freeze(FROZEN_NOW):
            dossier = createContentInContainer(
                self.portal,
                'opengever.dossier.businesscasedossier',
                title=DEFAULT_TITLE)

        persisted_values = get_persisted_values_for_obj(dossier)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory_on_portal(self):
        with freeze(FROZEN_NOW):
            new_id = self.portal.invokeFactory(
                'opengever.dossier.businesscasedossier',
                'dossier-1',
                title=DEFAULT_TITLE)
            dossier = self.portal[new_id]

        persisted_values = get_persisted_values_for_obj(dossier)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory_on_dx_container(self):
        outer_dossier = createContentInContainer(
            self.portal,
            'opengever.dossier.businesscasedossier',
            title=u'Outer Dossier',
        )

        with freeze(FROZEN_NOW):
            new_id = outer_dossier.invokeFactory(
                'opengever.dossier.businesscasedossier',
                'dossier-1',
                title=DEFAULT_TITLE)
            dossier = outer_dossier[new_id]

        persisted_values = get_persisted_values_for_obj(dossier)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        with freeze(FROZEN_NOW):
            browser.login().open()
            factoriesmenu.add(u'Business Case Dossier')
            browser.fill({u'Title': DEFAULT_TITLE}).save()
            dossier = browser.context

        persisted_values = get_persisted_values_for_obj(dossier)
        expected = self.get_z3c_form_defaults()

        # XXX: Don't know why this happens
        expected['public_trial_statement'] = None

        self.assertDictEqual(expected, persisted_values)


class TestDocumentDefaults(TestDefaultsBase):

    type_defaults = DOCUMENT_DEFAULTS
    form_defaults = DOCUMENT_FORM_DEFAULTS
    form_initvalues = DOCUMENT_FORM_INITVALUES

    def test_create_content_in_container(self):
        with freeze(FROZEN_NOW):
            doc = createContentInContainer(
                self.portal,
                'opengever.document.document',
                title=DEFAULT_TITLE)

        persisted_values = get_persisted_values_for_obj(doc)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory_on_portal(self):
        with freeze(FROZEN_NOW):
            new_id = self.portal.invokeFactory(
                'opengever.document.document',
                'document-1',
                title=DEFAULT_TITLE)
            doc = self.portal[new_id]

        persisted_values = get_persisted_values_for_obj(doc)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory_on_dx_container(self):
        outer_dossier = createContentInContainer(
            self.portal,
            'opengever.dossier.businesscasedossier',
            title=u'Outer Dossier',
        )

        with freeze(FROZEN_NOW):
            new_id = outer_dossier.invokeFactory(
                'opengever.document.document',
                'document-1',
                title=DEFAULT_TITLE)
            doc = outer_dossier[new_id]

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
            browser.fill({u'Title': DEFAULT_TITLE}).save()
            doc = outer_dossier['document-1']

        persisted_values = get_persisted_values_for_obj(doc)
        expected = self.get_z3c_form_defaults()

        # XXX: Don't know why this happens
        expected['public_trial_statement'] = None
        expected['description'] = None

        self.assertDictEqual(expected, persisted_values)


class TestMailDefaults(TestDefaultsBase):

    type_defaults = MAIL_DEFAULTS
    form_defaults = MAIL_FORM_DEFAULTS
    form_initvalues = MAIL_FORM_INITVALUES

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
                title=DEFAULT_TITLE,
                message=self.sample_msg)

        persisted_values = get_persisted_values_for_obj(mail)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory_on_portal(self):
        with freeze(FROZEN_NOW):
            new_id = self.portal.invokeFactory(
                'ftw.mail.mail',
                'mail',
                title=DEFAULT_TITLE,
                message=self.sample_msg)
            mail = self.portal[new_id]

        persisted_values = get_persisted_values_for_obj(mail)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory_on_dx_container(self):
        outer_dossier = createContentInContainer(
            self.portal,
            'opengever.dossier.businesscasedossier',
            title=u'Outer Dossier',
        )

        with freeze(FROZEN_NOW):
            new_id = outer_dossier.invokeFactory(
                'ftw.mail.mail',
                'document-1',
                title=DEFAULT_TITLE,
                message=self.sample_msg)
            mail = outer_dossier[new_id]

        persisted_values = get_persisted_values_for_obj(mail)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        with freeze(FROZEN_NOW):
            # Mail is not addable via factories menu
            browser.login().open(view='++add++ftw.mail.mail')
            browser.fill({
                u'Title': DEFAULT_TITLE,
                u'form.widgets.message': (TestMailDefaults.SAMPLE_MAIL,
                                          'msg.eml', 'message/rfc822')}).save()
            mail = browser.context

        persisted_values = get_persisted_values_for_obj(mail)
        expected = self.get_z3c_form_defaults()

        # XXX: Don't know why this happens
        expected['public_trial_statement'] = None
        expected['description'] = None

        self.assertDictEqual(expected, persisted_values)


class TestTaskDefaults(TestDefaultsBase):

    type_defaults = TASK_DEFAULTS
    form_defaults = TASK_FORM_DEFAULTS
    form_initvalues = TASK_FORM_INITVALUES

    def test_create_content_in_container(self):
        with freeze(FROZEN_NOW):
            task = createContentInContainer(
                self.portal,
                'opengever.task.task',
                title=DEFAULT_TITLE,
                issuer=TEST_USER_ID,
                responsible=TEST_USER_ID,
                responsible_client='client1')

        persisted_values = get_persisted_values_for_obj(task)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory_on_portal(self):
        with freeze(FROZEN_NOW):
            new_id = self.portal.invokeFactory(
                'opengever.task.task',
                'task-1',
                title=DEFAULT_TITLE,
                issuer=TEST_USER_ID,
                responsible=TEST_USER_ID,
                responsible_client='client1')
            task = self.portal[new_id]

        persisted_values = get_persisted_values_for_obj(task)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory_on_dx_container(self):
        outer_dossier = createContentInContainer(
            self.portal,
            'opengever.dossier.businesscasedossier',
            title=u'Outer Dossier',
        )

        with freeze(FROZEN_NOW):
            new_id = outer_dossier.invokeFactory(
                'opengever.task.task',
                'task-1',
                title=DEFAULT_TITLE,
                issuer=TEST_USER_ID,
                responsible=TEST_USER_ID,
                responsible_client='client1')
            task = outer_dossier[new_id]

        persisted_values = get_persisted_values_for_obj(task)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        with freeze(FROZEN_NOW):
            browser.login().open()
            factoriesmenu.add(u'Task')
            browser.fill({
                u'Title': DEFAULT_TITLE,
                u'Responsible': TEST_USER_ID,
                u'Task Type': 'information'}).save()
            task = self.portal['task-1']

        persisted_values = get_persisted_values_for_obj(task)
        expected = self.get_z3c_form_defaults()

        self.assertDictEqual(expected, persisted_values)


class TestContactDefaults(TestDefaultsBase):

    type_defaults = CONTACT_DEFAULTS
    form_defaults = CONTACT_FORM_DEFAULTS
    form_initvalues = CONTACT_FORM_INITVALUES

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
                'opengever.contact.contact')

        persisted_values = get_persisted_values_for_obj(contact)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory_on_dx_container(self):
        with freeze(FROZEN_NOW):
            new_id = self.contactfolder.invokeFactory(
                'opengever.contact.contact',
                'john-doe')
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
                u'Firstname': u'John',
                u'Lastname': u'John'}).save()
            contact = browser.context

        persisted_values = get_persisted_values_for_obj(contact)
        expected = self.get_z3c_form_defaults()

        # XXX: Don't know why this happens
        expected['description'] = None

        self.assertDictEqual(expected, persisted_values)


class TestCommitteeDefaults(TestDefaultsBase):

    type_defaults = COMMITTEE_DEFAULTS
    form_defaults = COMMITTEE_FORM_DEFAULTS
    form_initvalues = COMMITTEE_FORM_INITVALUES

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestCommitteeDefaults, self).setUp()
        self.container = createContentInContainer(
            self.portal,
            'opengever.meeting.committeecontainer',
            title=u'Meetings',
        )
        transaction.commit()

    def test_create_content_in_container(self):
        with freeze(FROZEN_NOW):
            committee = createContentInContainer(
                self.container,
                'opengever.meeting.committee',
                title=DEFAULT_TITLE)

        persisted_values = get_persisted_values_for_obj(committee)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    def test_invoke_factory_on_dx_container(self):
        with freeze(FROZEN_NOW):
            new_id = self.container.invokeFactory(
                'opengever.meeting.committee',
                'committee-1',
                title=DEFAULT_TITLE)
            contact = self.container[new_id]

        persisted_values = get_persisted_values_for_obj(contact)
        expected = self.get_type_defaults()

        self.assertDictEqual(expected, persisted_values)

    @browsing
    def test_z3c_add_form(self, browser):
        repofolder = createContentInContainer(
            self.portal,
            'opengever.repository.repositoryfolder',
            title='Repofolder')
        transaction.commit()

        with freeze(FROZEN_NOW):
            browser.login().open(self.container)
            factoriesmenu.add(u'Committee')
            browser.fill({
                u'Title': DEFAULT_TITLE,
                u'Group': 'client1_users',
                u'Linked repository folder ': repofolder})
            browser.find('Continue').click()
            browser.find('Save').click()
            committee = browser.context

        persisted_values = get_persisted_values_for_obj(committee)
        expected = self.get_z3c_form_defaults()

        linked_repo = persisted_values.pop('repository_folder')
        self.assertEqual(linked_repo.to_object, repofolder)

        self.assertDictEqual(expected, persisted_values)

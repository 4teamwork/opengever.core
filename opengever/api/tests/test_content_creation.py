from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.testbrowser import browsing
from opengever.api.add import get_validation_errors
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.oguid import Oguid
from opengever.base.response import IResponseContainer
from opengever.dossier.behaviors.dossier import IDossier
from opengever.repository.interfaces import IRepositoryFolder
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from plone import api
from plone.supermodel.model import Schema
from plone.uuid.interfaces import IUUID
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Invalid
from zope.interface import invariant
from zope.schema._bootstrapinterfaces import WrongType
from zope.schema.interfaces import RequiredMissing
import json


class TestSchema(Schema):

    first_field = schema.TextLine(
        title=u'first',
        required=True,
    )

    second_field = schema.TextLine(
        title=u'second',
        required=False,
    )

    @invariant
    def fields_are_different(data):
        if data.first_field == data.second_field:
            raise Invalid("first_field and second_field must be different")


class TestContext(object):
    """test class used as context for schema validation
    """


class TestSchemaValidation(FunctionalTestCase):

    def test_values_validation(self):
        context = TestContext()

        # validation succeeds with valid values
        data = {'first_field': u'valid value'}
        errors = get_validation_errors(context, data, TestSchema)
        self.assertEqual([], errors)

        # error is returned when value is invalid
        data = {'first_field': 1}
        errors = get_validation_errors(context, data, TestSchema)
        self.assertEqual(1, len(errors))
        field, error = errors[0]
        self.assertEqual('first_field', field)
        self.assertIsInstance(error, WrongType)

    def test_required_fields_validation(self):
        context = TestContext()

        data = {}
        errors = get_validation_errors(context, data, TestSchema)

        self.assertEqual(1, len(errors))
        field, error = errors[0]
        self.assertEqual('first_field', field)
        self.assertIsInstance(error, RequiredMissing)

    def test_invariant_validation(self):
        context = TestContext()

        data = {'first_field': u'valid value', 'second_field': u'valid value'}
        errors = get_validation_errors(context, data, TestSchema)

        self.assertEqual(1, len(errors))
        field, error = errors[0]
        self.assertIsInstance(error, Invalid)
        self.assertEqual('first_field and second_field must be different',
                         error.message)


class ITestRepositoryFolder(IRepositoryFolder):
    """Marker interface to register FolderPost for testing purposes
    """


class TestFolderPost(IntegrationTestCase):
    """ Tests the refactored FolderPost method
    """
    def setUp(self):
        super(TestFolderPost, self).setUp()
        self.portal = self.layer['portal']

        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')
        lang_tool.supported_langs = ['fr-ch', 'de-ch']

        self.layer['load_zcml_string'](
            '<configure '
            '    xmlns="http://namespaces.zope.org/zope"'
            '    xmlns:plone="http://namespaces.plone.org/plone"'
            '    xmlns:zcml="http://namespaces.zope.org/zcml"'
            '    xmlns:i18n="http://namespaces.zope.org/i18n"'
            '>'
            '<include package="plone.rest" file="meta.zcml" />'
            '    <plone:service '
            '        method="POST" '
            '        for="opengever.api.tests.test_content_creation.ITestRepositoryFolder" '
            '        factory="opengever.api.add.FolderPost" '
            '        permission="cmf.AddPortalContent" '
            '    /> '
            '</configure> '
            )

    @browsing
    def test_dossier_creation(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            u'@type': u'opengever.dossier.businesscasedossier',
            u'title': u'Sanierung B\xe4rengraben 2016',
            u'responsible': self.regular_user.id,
            u'custody_period': 30,
            u'archival_value': u'unchecked',
            u'retention_period': 5,
        }

        alsoProvides(self.leaf_repofolder, ITestRepositoryFolder)

        response = browser.open(
            self.leaf_repofolder.absolute_url(),
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(201, response.status_code)

        new_object_id = str(response.json['id'])
        dossier = self.leaf_repofolder.restrictedTraverse(new_object_id)

        self.assertEqual(u'Sanierung B\xe4rengraben 2016', dossier.title)
        self.assertEqual(self.regular_user.id, IDossier(dossier).responsible)
        self.assertEqual(30, ILifeCycle(dossier).custody_period)
        self.assertEqual(u'unchecked', ILifeCycle(dossier).archival_value)
        self.assertEqual(5, ILifeCycle(dossier).retention_period)


class TestContentCreation(IntegrationTestCase):

    features = ('meeting',)

    def setUp(self):
        super(TestContentCreation, self).setUp()
        self.portal = self.layer['portal']

        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')
        lang_tool.supported_langs = ['fr-ch', 'de-ch']

    @browsing
    def test_dossier_creation(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            u'@type': u'opengever.dossier.businesscasedossier',
            u'title': u'Sanierung B\xe4rengraben 2016',
            u'responsible': self.regular_user.id,
            u'custody_period': 30,
            u'archival_value': u'unchecked',
            u'retention_period': 5,
        }
        response = browser.open(
            self.leaf_repofolder.absolute_url(),
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(201, response.status_code)

        new_object_id = str(response.json['id'])
        dossier = self.leaf_repofolder.restrictedTraverse(new_object_id)

        self.assertEqual(u'Sanierung B\xe4rengraben 2016', dossier.title)
        self.assertEqual(self.regular_user.id, IDossier(dossier).responsible)
        self.assertEqual(30, ILifeCycle(dossier).custody_period)
        self.assertEqual(u'unchecked', ILifeCycle(dossier).archival_value)
        self.assertEqual(5, ILifeCycle(dossier).retention_period)

    @browsing
    def test_document_creation(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            u'@type': u'opengever.document.document',
            u'title': u'Sanierung B\xe4rengraben 2016',
            u'file': {
                u'data': u'TG9yZW0gSXBzdW0uCg==',
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
        self.assertEqual(u'Sanierung B\xe4rengraben 2016', doc.title)
        self.assertEqual(u'Sanierung Baerengraben 2016.txt', doc.file.filename)

        checksum = IBumblebeeDocument(doc).get_checksum()
        self.assertIsNotNone(checksum)

    @browsing
    def test_proposal_creation(self, browser):
        self.login(self.meeting_user, browser)

        committee_oguid = Oguid.for_object(self.committee).id
        payload = {
            u'@type': u'opengever.meeting.proposal',
            u'title': u'Sanierung B\xe4rengraben 2016',
            u'proposal_template': IUUID(self.proposal_template),
            u"committee_oguid": committee_oguid,
            u'issuer': self.meeting_user.getId(),
        }
        response = browser.open(
            self.dossier.absolute_url(),
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(201, response.status_code)

        new_object_id = str(response.json['id'])
        proposal = self.dossier.restrictedTraverse(new_object_id)
        self.assertEqual(u'Sanierung B\xe4rengraben 2016', proposal.title)
        self.assertEqual(self.meeting_user.getId(), proposal.issuer)

        proposal_doc = proposal.get_proposal_document()
        self.assertIsNotNone(proposal_doc)
        self.assertEqual(u'Sanierung B\xe4rengraben 2016',
                         proposal_doc.title)
        self.assertEqual(u'Sanierung Baerengraben 2016.docx',
                         proposal_doc.get_filename())

        checksum = IBumblebeeDocument(proposal_doc).get_checksum()
        self.assertIsNotNone(checksum)
        self.assertEqual(IBumblebeeDocument(self.proposal_template).get_checksum(),
                         checksum)

        # Creating a proposal should generate a history entry
        responses = IResponseContainer(proposal).list()
        self.assertEqual(1, len(responses))
        self.assertEqual('created', responses[0].response_type)

    @browsing
    def test_template_is_mandatory_for_proposal_creation(self, browser):
        self.login(self.meeting_user, browser)

        committee_oguid = Oguid.for_object(self.committee).id
        payload = {
            u'@type': u'opengever.meeting.proposal',
            u'title': u'Sanierung B\xe4rengraben 2016',
            u"committee_oguid": committee_oguid,
            u'issuer': self.meeting_user.getId(),
        }

        with browser.expect_http_error():
            browser.open(
                self.dossier.absolute_url(),
                data=json.dumps(payload),
                method='POST',
                headers=self.api_headers)

        self.assertEqual(400, browser.status_code)
        self.assertDictEqual(
            {u'message': u"[(None, Invalid(u'error_template_or_document_required_for_creation',))]",
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_proposal_creation_from_docx_template(self, browser):
        self.login(self.meeting_user, browser)

        committee_oguid = Oguid.for_object(self.committee).id
        payload = {
            u'@type': u'opengever.meeting.proposal',
            u'title': u'Sanierung B\xe4rengraben 2016',
            u'proposal_document_type': 'existing',
            u'proposal_document': IUUID(self.document),
            u"committee_oguid": committee_oguid,
            u'issuer': self.meeting_user.getId(),
        }

        response = browser.open(
            self.dossier.absolute_url(),
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(201, response.status_code)

        new_object_id = str(response.json['id'])
        proposal = self.dossier.restrictedTraverse(new_object_id)
        self.assertEqual(u'Sanierung B\xe4rengraben 2016', proposal.title)
        self.assertEqual(self.meeting_user.getId(), proposal.issuer)

        proposal_doc = proposal.get_proposal_document()
        self.assertIsNotNone(proposal_doc)
        self.assertEqual(u'Sanierung B\xe4rengraben 2016',
                         proposal_doc.title)
        self.assertEqual(u'Sanierung Baerengraben 2016.docx',
                         proposal_doc.get_filename())

        checksum = IBumblebeeDocument(proposal_doc).get_checksum()
        self.assertIsNotNone(checksum)
        self.assertEqual(IBumblebeeDocument(self.document).get_checksum(),
                         checksum)

    @browsing
    def test_proposal_creation_from_predecessor_proposal_document(self, browser):
        self.login(self.meeting_user, browser)

        committee_oguid = Oguid.for_object(self.committee).id
        payload = {
            u'@type': u'opengever.meeting.proposal',
            u'title': u'Sanierung B\xe4rengraben 2016',
            u'proposal_template': IUUID(self.proposal.get_proposal_document()),
            u'predecessor_proposal': IUUID(self.proposal),
            u"committee_oguid": committee_oguid,
            u'issuer': self.meeting_user.getId(),
        }

        response = browser.open(
            self.dossier.absolute_url(),
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(201, response.status_code)

        new_object_id = str(response.json['id'])
        proposal = self.dossier.restrictedTraverse(new_object_id)
        self.assertEqual(u'Sanierung B\xe4rengraben 2016', proposal.title)
        self.assertEqual(self.meeting_user.getId(), proposal.issuer)

        proposal_doc = proposal.get_proposal_document()
        self.assertIsNotNone(proposal_doc)
        self.assertEqual(u'Sanierung B\xe4rengraben 2016',
                         proposal_doc.title)
        self.assertEqual(u'Sanierung Baerengraben 2016.docx',
                         proposal_doc.get_filename())

        checksum = IBumblebeeDocument(proposal_doc).get_checksum()
        self.assertIsNotNone(checksum)
        self.assertEqual(
            IBumblebeeDocument(self.proposal.get_proposal_document()).get_checksum(),
            checksum)

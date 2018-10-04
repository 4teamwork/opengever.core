from datetime import datetime
from datetime import time
from ooxml_docprops import is_supported_mimetype
from ooxml_docprops.properties import OOXMLDocument
from opengever import journal
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.base.vocabulary import voc_term_title
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.document import IDocumentSchema
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.interfaces import IDocProperties
from opengever.dossier.interfaces import IDocPropertyProvider
from opengever.dossier.interfaces import ITemplateFolderProperties
from opengever.ogds.base.utils import ogds_service
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import IMemberData
from Products.CMFCore.utils import getToolByName
from tempfile import NamedTemporaryFile
from zope.component import adapter
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryAdapter
from zope.event import notify
from zope.interface import implementer
from zope.lifecycleevent import ObjectModifiedEvent
from zope.publisher.interfaces.browser import IBrowserRequest
import os


class TemporaryDocFile(object):

    def __init__(self, file_):
        self.file = file_
        self.path = None

    def __enter__(self):
        template_data = self.file.data

        with NamedTemporaryFile(delete=False) as tmpfile:
            self.path = tmpfile.name
            tmpfile.write(template_data)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self.path)


class DocPropertyWriter(object):
    """Write doc-properties for a document.

    The optional argument recipient_data is an iterable of doc-property
    providers that are added to the document with a "recipient" prefix.
    """

    def __init__(self, document, recipient_data=tuple()):
        self.recipient_data = recipient_data
        self.document = document
        self.request = self.document.REQUEST

    def update(self):
        if self.update_doc_properties(only_existing=True):
            journal.handlers.doc_properties_updated(self.document)

    def initialize(self):
        self.update_doc_properties(only_existing=False)

    def get_properties(self):
        properties_adapter = getMultiAdapter(
            (self.document, self.request), IDocProperties)
        return properties_adapter.get_properties(self.recipient_data)

    def is_export_enabled(self):
        registry = getUtility(IRegistry)
        props = registry.forInterface(ITemplateFolderProperties)
        return props.create_doc_properties

    def update_doc_properties(self, only_existing):
        if not self.is_export_enabled():
            return False
        if not self.has_file():
            return False
        if not self.is_supported_file():
            return False

        return self.write_properties(only_existing, self.get_properties())

    def write_properties(self, only_existing, properties):
        with TemporaryDocFile(self.document.file) as tmpfile:
            changed = False

            with OOXMLDocument(tmpfile.path, force=True) as doc:
                if only_existing:
                    if doc.has_any_property(properties.keys()):
                        doc.update_properties(properties)
                        changed = True
                else:
                    doc.update_properties(properties)
                    changed = True

            if changed:
                with open(tmpfile.path) as processed_tmpfile:
                    file_data = processed_tmpfile.read()

                self.document.update_file(file_data)
                notify(ObjectModifiedEvent(self.document))

            return changed

    def has_file(self):
        return self.document.file is not None

    def is_supported_file(self):
        return is_supported_mimetype(self.document.file.contentType)


@implementer(IDocPropertyProvider)
class DocPropertyProvider(object):
    """Baseclass for DocPropertyProviders.

    Contains utility methods to create a dict of doc-properties. Set the NS
    class attribute to define a namespace. All your property-values written
    with _add_property will be prefixed with that namespace.
    """

    NS = tuple()

    def __init__(self, context):
        self.context = context

    def _add_property(self, properties, name, value):
        """Add single property to collection of properties.

        If a namespace (NS) has been configured prefixes keys with that
        namespace.
        """
        if value is None:
            return
        key = '.'.join(self.NS + (name,))
        properties[key] = value

    def get_properties(self):
        return {}

    def get_title(self):
        return self.context.title

    def get_reference_number(self):
        return getAdapter(self.context, IReferenceNumber).get_number()

    def get_sequence_number(self):
        return str(getUtility(ISequenceNumber).get_number(self.context))


@adapter(IDocumentSchema)
class DefaultDocumentDocPropertyProvider(DocPropertyProvider):
    """
    """

    NS = ('ogg', 'document')

    def _as_datetime(self, date):
        if not date:
            return date

        return datetime.combine(date, time(0, 0))

    def get_document_author(self):
        return IDocumentMetadata(self.context).document_author

    def get_document_date(self):
        return self._as_datetime(
            IDocumentMetadata(self.context).document_date)

    def get_document_type_label(self):
        return voc_term_title(
            IDocumentMetadata['document_type'],
            IDocumentMetadata(self.context).document_type)

    def get_reception_date(self):
        return self._as_datetime(
            IDocumentMetadata(self.context).receipt_date)

    def get_delivery_date(self):
        return self._as_datetime(
            IDocumentMetadata(self.context).delivery_date)

    def get_document_version(self):
        return IDocumentMetadata(self.context).get_current_version_id(missing_as_zero=True)

    def get_properties(self):
        """Return document properties.

        XXX Also contains deprecated properties that will go away eventually.
        """

        reference_number = self.get_reference_number()
        sequence_number = str(self.get_sequence_number())

        # XXX deprecated properties
        properties = {'Document.ReferenceNumber': reference_number,
                      'Document.SequenceNumber': sequence_number}

        self._add_property(properties, 'title', self.get_title())
        self._add_property(properties, 'reference_number', reference_number)
        self._add_property(properties, 'sequence_number', sequence_number)
        self._add_property(properties, 'document_author', self.get_document_author())
        self._add_property(properties, 'document_date', self.get_document_date())
        self._add_property(properties, 'document_type', self.get_document_type_label())
        self._add_property(properties, 'reception_date', self.get_reception_date())
        self._add_property(properties, 'delivery_date', self.get_delivery_date())
        self._add_property(properties, 'version_number', self.get_document_version())

        return properties


@adapter(IDossierMarker)
class DefaultDossierDocPropertyProvider(DocPropertyProvider):
    """Return the default dossier properties"""

    NS = ('ogg', 'dossier')

    def get_external_reference(self):
        return IDossier(self.context).external_reference

    def get_properties(self):
        """Return dossier properties.

        XXX Also contains deprecated properties that will go away eventually.
        """
        reference_number = self.get_reference_number()
        sequence_number = self.get_sequence_number()
        title = self.get_title()

        # XXX deprecated properties
        properties = {'Dossier.ReferenceNumber': reference_number,
                      'Dossier.Title': title}

        self._add_property(properties, 'title', title)
        self._add_property(properties, 'reference_number', reference_number)
        self._add_property(properties, 'sequence_number', sequence_number)
        self._add_property(properties, 'external_reference', self.get_external_reference())

        return properties


@adapter(IMemberData)
class DefaultMemberDocPropertyProvider(DocPropertyProvider):
    """Return the default user properties from LDAP/ogds."""

    NS = ('ogg', 'user')

    ogds_user_attributes = (
        'firstname',
        'lastname',
        'directorate',
        'directorate_abbr',
        'department',
        'department_abbr',
        'email',
        'email2',
        'url',
        'phone_office',
        'phone_fax',
        'phone_mobile',
        'salutation',
        'description',
        'address1',
        'address2',
        'zip_code',
        'city',
        'country'
    )

    def get_user_id(self):
        return self.context.getMemberId()

    def get_properties(self):
        """Return user properties from OGDS.

        Always returns a minimal set of the properties 'ogg.user.userid' and
        'ogg.user.title' even when no ogds-user is found.

        XXX Also contains deprecated properties that will go away eventually.
        """
        user_id = self.get_user_id()
        ogds_user = ogds_service().fetch_user(user_id)
        fullname = ogds_user.fullname() if ogds_user else user_id

        # XXX deprecated properties
        properties = {'User.ID': user_id,
                      'User.FullName': fullname}

        self._add_property(properties, 'userid', user_id)
        self._add_property(properties, 'title', fullname)

        # abort early if there is no ogds user for some reason.
        if not ogds_user:
            return properties

        for attribute_name in self.ogds_user_attributes:
            value = getattr(ogds_user, attribute_name)
            self._add_property(properties, attribute_name, value)
        return properties


@implementer(IDocProperties)
@adapter(IDocumentSchema, IBrowserRequest)
class DefaultDocProperties(object):

    def __init__(self, context, request):
        # Context is the newly created document
        self.context = context
        self.request = request

    def get_repofolder(self, dossier):
        return None

    def get_repo(self, dossier):
        return None

    def get_site(self, dossier):
        return None

    def get_member(self, request):
        portal_membership = getToolByName(self.context, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        return member

    def get_properties(self, recipient_data=tuple()):
        document = self.context
        dossier = document.get_parent_dossier()
        repofolder = self.get_repofolder(dossier)
        repo = self.get_repo(dossier)
        site = self.get_site(dossier)
        member = self.get_member(self.request)
        proposal = document.get_proposal()

        properties = {}
        for obj in [document, dossier, repofolder, repo, site, member, proposal]:
            property_provider = queryAdapter(obj, IDocPropertyProvider)
            obj_properties = {}
            if property_provider is not None:
                obj_properties = property_provider.get_properties()
            properties.update(obj_properties)

        for recipient in recipient_data:
            provider = recipient.get_doc_property_provider(prefix='recipient')
            properties.update(provider.get_properties())

        return properties

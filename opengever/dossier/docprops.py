from datetime import datetime
from datetime import time
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.base.vocabulary import voc_term_title
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.document import IDocumentSchema
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.interfaces import IDocPropertyProvider
from opengever.ogds.base.utils import ogds_service
from Products.CMFCore.interfaces import IMemberData
from zope.component import adapter
from zope.component import getAdapter
from zope.component import getUtility
from zope.interface import implementer


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

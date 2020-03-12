from datetime import datetime
from datetime import time
from opengever.base.docprops import BaseDocPropertyProvider
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.base.vocabulary import voc_term_title
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.document import IDocumentSchema
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.ogds.models.service import ogds_service
from Products.CMFCore.interfaces import IMemberData
from zope.component import adapter
from zope.component import getAdapter
from zope.component import getUtility


class DocPropertyProvider(BaseDocPropertyProvider):
    """Baseclass for DocPropertyProviders for plone content."""

    def get_title(self):
        return self.context.title

    def get_reference_number(self):
        return getAdapter(self.context, IReferenceNumber).get_number()

    def get_sequence_number(self):
        return str(getUtility(ISequenceNumber).get_number(self.context))

    def _collect_deprectated_properties(self):
        return dict()

    def get_properties(self, prefix=None):
        properties = super(DocPropertyProvider, self).get_properties(
            prefix=prefix)
        if not prefix:
            properties = self._merge(
                properties, self._collect_deprectated_properties())
        return properties


@adapter(IDocumentSchema)
class DefaultDocumentDocPropertyProvider(DocPropertyProvider):

    DEFAULT_PREFIX = ('document',)

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

    def _collect_properties(self):
        return {
            'title': self.get_title(),
            'reference_number': self.get_reference_number(),
            'sequence_number': self.get_sequence_number(),
            'document_author': self.get_document_author(),
            'document_date': self.get_document_date(),
            'document_type': self.get_document_type_label(),
            'reception_date': self.get_reception_date(),
            'delivery_date': self.get_delivery_date(),
            'version_number': self.get_document_version(),
        }

    def _collect_deprectated_properties(self):
        return {
            'Document.ReferenceNumber': self.get_reference_number(),
            'Document.SequenceNumber': self.get_sequence_number()
        }


@adapter(IDossierMarker)
class DefaultDossierDocPropertyProvider(DocPropertyProvider):
    """Return the default dossier properties"""

    DEFAULT_PREFIX = ('dossier',)

    def get_external_reference(self):
        return IDossier(self.context).external_reference

    def _collect_properties(self):
        return {
            'title': self.get_title(),
            'reference_number': self.get_reference_number(),
            'sequence_number': self.get_sequence_number(),
            'external_reference': self.get_external_reference(),
        }

    def _collect_deprectated_properties(self):
        return {
            'Dossier.ReferenceNumber': self.get_reference_number(),
            'Dossier.Title': self.get_title(),
        }


@adapter(IMemberData)
class DefaultMemberDocPropertyProvider(DocPropertyProvider):
    """Return the default user properties from LDAP/ogds."""

    DEFAULT_PREFIX = ('user',)

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

    def __init__(self, context):
        super(DefaultMemberDocPropertyProvider, self).__init__(context)
        self.user_id = self.context.getMemberId()
        self.ogds_user = ogds_service().fetch_user(self.user_id)

    def get_fullname(self):
        return self.ogds_user.fullname() if self.ogds_user else self.user_id

    def _collect_properties(self):
        """Return user properties from OGDS.

        Always returns a minimal set of the properties 'ogg.user.userid' and
        'ogg.user.title' even when no ogds-user is found.
        """
        properties = {
            'userid': self.user_id,
            'title': self.get_fullname()
        }
        if not self.ogds_user:
            return properties

        for attribute_name in self.ogds_user_attributes:
            value = getattr(self.ogds_user, attribute_name)
            properties[attribute_name] = value
        return properties

    def _collect_deprectated_properties(self):
        return {
            'User.ID': self.user_id,
            'User.FullName': self.get_fullname(),
        }

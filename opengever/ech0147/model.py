"""eCH-0147T1 model"""
from datetime import datetime
from opengever.base.behaviors.classification import IClassification
from opengever.base.interfaces import IReferenceNumber
from opengever.base.utils import file_checksum
from opengever.document.behaviors import IBaseDocument
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.ech0147.bindings import ech0039
from opengever.ech0147.bindings import ech0058
from opengever.ech0147.bindings import ech0147t0
from opengever.ech0147.bindings import ech0147t1
from opengever.ech0147.mappings import CLASSIFICATION_MAPPING
from opengever.ech0147.mappings import DOSSIER_STATUS_MAPPING
from opengever.ech0147.mappings import PRIVACY_LAYER_MAPPING
from opengever.ech0147.mappings import PUBLIC_TRIAL_MAPPING
from plone import api
from Products.CMFCore.utils import getToolByName
from pyxb.utils.domutils import BindingDOMSupport
from uuid import uuid4
import os.path
import pkg_resources


BindingDOMSupport.DeclareNamespace(ech0147t1.Namespace, 'eCH-0147T1')
BindingDOMSupport.DeclareNamespace(ech0147t0.Namespace, 'eCH-0147T0')
BindingDOMSupport.DeclareNamespace(ech0039.Namespace, 'eCH-0039')
BindingDOMSupport.DeclareNamespace(ech0058.Namespace, 'eCH-0058')


class MessageT1(object):
    """eCH-0147T1 message"""

    def __init__(self):
        self.directive = None
        self.dossiers = []
        self.documents = []
        self.addresses = []

        self.action = 1
        self.test_delivery_flag = False

        user = api.user.get_current()
        email = user.getProperty('email').decode('utf8')
        if email:
            self.sender_id = email
        else:
            self.sender_id = user.getId()

        # Sending application
        self.app_manufacturer = u'4teamwork AG'
        self.app_name = u'OneGov GEVER'
        self.app_version = pkg_resources.get_distribution(
            "opengever.core").version.decode('utf8')[:10]

        self.message_id = unicode(uuid4())
        self.message_date = datetime.now()

        # Optional properties
        self.recipient_id = None
        self.original_sender_id = None
        self.declaration_local_reference = None
        self.reference_message_id = None
        self.unique_business_transaction_id = None
        self.our_business_transaction_id = None
        self.your_business_transaction_id = None
        self.initial_message_date = None
        self.event_date = None
        self.event_period = None
        self.modification_date = None
        self.subjects = []
        self.comments = []

    def add_object(self, obj):
        if IDossierMarker.providedBy(obj):
            self.dossiers.append(Dossier(obj, u'files'))
        elif IBaseDocument.providedBy(obj) and obj.get_file():
            self.documents.append(Document(obj, u'files'))

    def binding(self):
        """Return XML binding"""
        m = ech0147t1.message()
        m.header = self.header()
        m.content_ = ech0147t1.contentType()
        if self.directive is not None:
            m.content_.directive = self.directive.binding()

        if self.dossiers:
            m.content_.dossiers = ech0147t0.dossiersType()
            for dossier in self.dossiers:
                m.content_.dossiers.append(dossier.binding())

        if self.documents:
            m.content_.documents = ech0147t0.documentsType()
            for document in self.documents:
                m.content_.documents.append(document.binding())

        if self.addresses:
            m.content_.addresses = ech0147t0.adressesType()
            for address in self.addresses:
                m.content_.addresses.append(address.binding())

        return m

    def header(self):
        h = ech0147t0.headerType()
        h.senderId = self.sender_id
        h.recipientId = self.recipient_id
        h.originalSenderId = self.original_sender_id
        h.declarationLocalReference = self.declaration_local_reference
        h.messageId = self.message_id
        h.referenceMessageId = self.reference_message_id
        h.uniqueBusinessTransactionId = self.unique_business_transaction_id
        h.ourBusinessTransactionId = self.our_business_transaction_id
        h.yourBusinessTransactionId = self.your_business_transaction_id

        h.messageType = 1
        h.subMessageType = None
        h.messageGroup = ech0039.messageGroupType(1, 1)
        h.sendingApplication = ech0058.sendingApplicationType(
            self.app_manufacturer, self.app_name, self.app_version)

        h.messageDate = self.message_date
        h.initialMessageDate = self.initial_message_date
        h.eventDate = self.event_date
        h.eventPeriod = self.event_period
        h.modificationDate = self.modification_date

        h.action = self.action
        h.testDeliveryFlag = self.test_delivery_flag

        if self.subjects:
            h.subjects = ech0039.subjectsType()
            for subject in self.subjects:
                h.subjects.append(ech0039.subjectType(subject))

        if self.comments:
            h.comments = ech0039.commentsType()
            for comment in self.comments:
                h.comments.append(ech0039.commentType(comment))

        return h

    def add_to_zip(self, zipfile):
        for dossier in self.dossiers:
            dossier.add_to_zip(zipfile)
        for document in self.documents:
            zipfile.write(document.committed_file_path(), document.path)


class Dossier(object):

    def __init__(self, obj, base_path):
        self.obj = obj
        self.path = os.path.join(base_path, self.obj.getId())

        self.dossiers = []
        self.documents = []
        self.folders = []

        self._add_descendants()

    def _add_descendants(self):
        objs = self.obj.objectValues()
        for obj in objs:
            if IDossierMarker.providedBy(obj):
                self.dossiers.append(Dossier(obj, self.path))
            elif IBaseDocument.providedBy(obj) and obj.get_file():
                self.documents.append(Document(obj, self.path))

    def binding(self):
        d = ech0147t0.dossierType()
        d.uuid = self.obj.UID()

        wftool = getToolByName(self.obj, "portal_workflow")
        status = wftool.getInfoFor(self.obj, 'review_state')
        d.status = DOSSIER_STATUS_MAPPING[status]

        d.titles = ech0039.titlesType()
        d.titles.append(
            ech0039.titleType(self.obj.Title().decode('utf8'), lang=u'DE'))

        c_obj = IClassification(self.obj)
        d.classification = ech0039.classificationType(
            CLASSIFICATION_MAPPING[c_obj.classification])
        d.hasPrivacyProtection = PRIVACY_LAYER_MAPPING[c_obj.privacy_layer]

        d.caseReferenceLocalId = IReferenceNumber(self.obj).get_number()

        dossier_obj = IDossier(self.obj)
        d.openingDate = dossier_obj.start

        if dossier_obj.keywords:
            d.keywords = ech0039.keywordsType()
            for keyword in dossier_obj.keywords:
                d.keywords.append(ech0039.keywordType(keyword, lang=u'DE'))

        if self.dossiers:
            d.dossiers = ech0147t0.dossiersType()
            for dossier in self.dossiers:
                d.dossiers.append(dossier.binding())

        if self.documents:
            d.documents = ech0147t0.documentsType()
            for document in self.documents:
                d.documents.append(document.binding())

        # Optional, currently not supported properties
        d.openToThePublic = None
        d.comments = None
        d.links = None
        d.folders = None
        d.addresses = None
        d.applicationCustom = None

        return d

    def add_to_zip(self, zipfile):
        for dossier in self.dossiers:
            dossier.add_to_zip(zipfile)
        for document in self.documents:
            zipfile.write(document.committed_file_path(), document.path)


class Document(object):

    def __init__(self, obj, base_path):
        self.obj = obj
        self.path = os.path.join(base_path, self.obj.get_file().filename)

    def committed_file_path(self):
        return self.obj.get_file()._blob.committed()

    def binding(self):
        d = ech0147t0.documentType()
        d.uuid = self.obj.UID()
        d.titles = ech0039.titlesType()
        d.titles.append(ech0039.titleType(
            self.obj.Title().decode('utf8'), lang=u'DE'))
        d.status = u'undefined'

        d.files = ech0147t0.filesType()
        f = ech0147t0.fileType()
        f.pathFileName = self.path
        f.mimeType = self.obj.get_file().contentType
        f.hashCodeAlgorithm, f.hashCode = file_checksum(self.committed_file_path())
        d.files.append(f)

        c_obj = IClassification(self.obj)
        d.classification = ech0039.classificationType(
            CLASSIFICATION_MAPPING[c_obj.classification])
        d.hasPrivacyProtection = PRIVACY_LAYER_MAPPING[c_obj.privacy_layer]
        d.openToThePublic = PUBLIC_TRIAL_MAPPING[c_obj.public_trial]

        md = IDocumentMetadata(self.obj)
        d.documentKind = md.document_type
        d.openingDate = md.document_date
        d.ourRecordReference = md.foreign_reference
        d.owner = md.document_author

        if md.keywords:
            d.keywords = ech0039.keywordsType()
            for keyword in md.keywords:
                d.keywords.append(ech0039.keywordType(keyword, lang=u'DE'))

        # Optional, currently not supported properties
        d.signer = None
        d.comments = None
        d.isLeadingDocument = None
        d.sortOrder = None
        d.applicationCustom = None

        return d


class Directive(object):

    def __init__(self, instruction):
        self.uuid = unicode(uuid4())
        self.instruction = instruction
        self.priority = u'undefined'
        self.deadline = None

    def binding(self):
        d = ech0147t1.directiveType()
        d.uuid = self.uuid
        d.instruction = self.instruction
        d.priority = self.priority
        d.deadline = self.deadline
        return d

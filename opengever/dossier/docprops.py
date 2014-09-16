from Acquisition import aq_parent
from five import grok
from ooxml_docprops import is_supported_mimetype
from ooxml_docprops.properties import OOXMLDocument
from opengever import journal
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.document.document import IDocumentSchema
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.interfaces import IDocProperties
from opengever.dossier.interfaces import IDocPropertyProvider
from opengever.dossier.interfaces import ITemplateDossierProperties
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import IMemberData
from Products.CMFCore.utils import getToolByName
from tempfile import NamedTemporaryFile
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryAdapter
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

    def __init__(self, document):
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
        return properties_adapter.get_properties()

    def is_export_enabled(self):
        registry = getUtility(IRegistry)
        props = registry.forInterface(ITemplateDossierProperties)
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

            with OOXMLDocument(tmpfile.path) as doc:
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
                self.document.file.data = file_data

            return changed

    def has_file(self):
        return self.document.file is not None

    def is_supported_file(self):
        return is_supported_mimetype(self.document.file.contentType)


class DefaultDocumentDocPropertyProvider(grok.Adapter):
    """
    """
    grok.context(IDocumentSchema)
    grok.provides(IDocPropertyProvider)

    def get_reference_number(self):
        ref_num = getAdapter(self.context, IReferenceNumber).get_number()
        return ref_num

    def get_sequence_number(self):
        return getUtility(ISequenceNumber).get_number(self.context)

    def get_properties(self):
        reference_number = self.get_reference_number()
        sequence_number = str(self.get_sequence_number())
        properties = {'Document.ReferenceNumber': reference_number,
                      'Document.SequenceNumber': sequence_number}
        return properties


class DefaultDossierDocPropertyProvider(grok.Adapter):
    """
    """
    grok.context(IDossierMarker)
    grok.provides(IDocPropertyProvider)

    def get_reference_number(self):
        ref_num = getAdapter(self.context, IReferenceNumber).get_number()
        return ref_num

    def get_title(self):
        return self.context.title.encode('utf-8')

    def get_properties(self):
        reference = self.get_reference_number()
        title = self.get_title()
        properties = {'Dossier.ReferenceNumber': reference,
                      'Dossier.Title': title}
        return properties


class DefaultMemberDocPropertyProvider(grok.Adapter):
    """
    """
    grok.context(IMemberData)
    grok.provides(IDocPropertyProvider)

    def get_user_id(self):
        return self.context.getMemberId()

    def get_fullname(self):
        return self.context.getProperty('fullname')

    def get_properties(self):
        user_id = self.get_user_id()
        fullname = self.get_fullname()
        properties = {'User.ID': user_id,
                      'User.FullName': fullname}
        return properties


class DefaultDocProperties(grok.MultiAdapter):
    grok.adapts(IDocumentSchema, IBrowserRequest)
    grok.implements(IDocProperties)

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

    def get_properties(self):
        document = self.context
        dossier = aq_parent(document)
        repofolder = self.get_repofolder(dossier)
        repo = self.get_repo(dossier)
        site = self.get_site(dossier)
        member = self.get_member(self.request)

        properties = {}
        for obj in [document, dossier, repofolder, repo, site, member]:
            property_provider = queryAdapter(obj, IDocPropertyProvider)
            obj_properties = {}
            if property_provider is not None:
                obj_properties = property_provider.get_properties()
            properties.update(obj_properties)
        return properties

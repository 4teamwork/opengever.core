from Acquisition import aq_parent
from five import grok
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.document.document import IDocumentSchema
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.interfaces import IDocProperties
from opengever.dossier.interfaces import IDocPropertyProvider
from Products.CMFCore.interfaces import IMemberData
from Products.CMFCore.utils import getToolByName
from zope.component import getAdapter
from zope.component import getUtility
from zope.component import queryAdapter
from zope.publisher.interfaces.browser import IBrowserRequest


class DefaultDocumentDocPropertyProvider(grok.Adapter):
    """
    """
    grok.context(IDocumentSchema)
    grok.provides(IDocPropertyProvider)

    def get_reference_number(self):
        ref_num = getAdapter(self.context, IReferenceNumber).get_number()
        return ref_num

    def get_sequence_number(self):
        return str(getUtility(ISequenceNumber).get_number(self.context))

    def get_properties(self):
        reference_number = self.get_reference_number()
        sequence_number = self.get_sequence_number()
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

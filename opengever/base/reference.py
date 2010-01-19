from Acquisition import aq_parent, aq_inner
from five import grok
from zope.interface import Interface
from zope.component import getUtility, queryAdapter

from Products.CMFCore.interfaces import ISiteRoot
from plone.dexterity.interfaces import IDexterityContent
from plone.registry.interfaces import IRegistry

from opengever.base.interfaces import IBaseClientID
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.repository.repositoryfolder import IRepositoryFolderSchema
from opengever.repository.repositoryroot import IRepositoryRoot
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.document.document import IDocumentSchema
import opengever.base.behaviors.reference


class BasicReferenceNumber(grok.Adapter):
    """ Basic reference number adapter
    """
    grok.provides(IReferenceNumber)
    grok.context(IDexterityContent)

    def get_number(self):
        return ''

    def get_parent_number(self):
        parent = aq_parent(aq_inner(self.context))
        parentRF = queryAdapter(parent, IReferenceNumber)
        if parentRF:
            return parentRF.get_number()
        else:
            return None
        

class PlatformReferenceNumber(BasicReferenceNumber):
    """ Reference number generator for the plone site
    """
    grok.provides(IReferenceNumber)
    grok.context(ISiteRoot)

    def get_number(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IBaseClientID)
        return getattr(proxy, 'client_id')


class IRepositoryRoot(BasicReferenceNumber):
    """ Reference number generator for the repository root, which just
    adds the seperator-space and is primary required because we wan't
    to traverse over it.
    """
    grok.provides(IReferenceNumber)
    grok.context(IRepositoryRoot)

    def get_number(self):
        parent_num = self.get_parent_number()
        if parent_num:
            return str(parent_num) + ' '
        return ''

 
class RepositoryFolderReferenceNumber(BasicReferenceNumber):
    """ Reference number for repository folder
    """
    grok.provides(IReferenceNumber)
    grok.context(IRepositoryFolderSchema)

    def get_number(self):
        # get local number prefix
        num = opengever.base.behaviors.reference.IReferenceNumber(
            self.context).reference_number
        num = num and str(num) or ''
        # get the parent number
        parent_num = self.get_parent_number()
        parent = aq_parent(aq_inner(self.context))
        if parent_num and IRepositoryFolderSchema.providedBy(parent):
            return str(parent_num) + '.' + num
        elif parent_num:
            return str(parent_num) + num
        else:
            return num

 
class DossierReferenceNumber(BasicReferenceNumber):
    """ Reference number for dossier types
    """
    grok.provides(IReferenceNumber)
    grok.context(IDossierMarker)

    def get_number(self):
        # get local number prefix
        num = opengever.base.behaviors.reference.IReferenceNumber(
            self.context).reference_number
        num = num and str(num) or ''
        # get the parent number
        parent_num = self.get_parent_number()
        parent = aq_parent(aq_inner(self.context))
        if parent_num and IDossierMarker.providedBy(parent):
            return str(parent_num) + '.' + num
        elif parent_num and IRepositoryFolderSchema.providedBy(parent):
            return str(parent_num) + ' / ' + num
        else:
            return num

 
class DocumentReferenceNumber(BasicReferenceNumber):
    """ Reference number for documents
    """
    grok.provides(IReferenceNumber)
    grok.context(IDocumentSchema)
    
    def get_number(self):
        # get local sequence_number
        sequenceNr = getUtility(ISequenceNumber)
        num = sequenceNr.get_number(self.context)
        num = num and str(num) or ''
        # get the parent number
        parent_num = self.get_parent_number()
        parent = aq_parent(aq_inner(self.context))
        if parent_num and IDossierMarker.providedBy(parent):
            return str(parent_num) + ' / ' + num
        else:
            return num


from Acquisition import aq_parent
from DateTime import DateTime
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.interfaces import IReferenceNumber
from opengever.disposition import _
from opengever.disposition.ech0160.bindings import arelda
from opengever.disposition.ech0160.model import Document
from opengever.disposition.ech0160.model import NOT_SPECIFIED
from opengever.disposition.ech0160.model.additional_data import get_additional_data
from opengever.disposition.ech0160.utils import set_classification_attributes
from opengever.document.behaviors import IBaseDocument
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.meeting.proposal import IProposal
from opengever.repository.repositoryroot import IRepositoryRoot
from opengever.task.task import ITask
from plone.dexterity.utils import safe_unicode
from Products.CMFCore.utils import getToolByName
from zope.globalrequest import getRequest
from zope.i18n import translate


class Dossier(object):
    """eCH-0160 dossierGeverSIP"""

    document_types = ['opengever.document.document', 'ftw.mail.mail']

    def __init__(self, obj):
        self.obj = obj
        self.dossiers = {}
        self.documents = {}
        self.folder = None

        self._add_descendants()

    def parents(self):
        obj = self.obj
        parents = [self]
        while True:
            obj = aq_parent(obj)
            parents.insert(0, obj)
            if obj is None or IRepositoryRoot.providedBy(obj):
                break
        return parents

    def _add_descendants(self):
        objs = self.obj.objectValues()
        for obj in objs:
            if IDossierMarker.providedBy(obj):
                self.dossiers[obj.UID()] = Dossier(obj)
            elif IBaseDocument.providedBy(obj):
                self.documents[obj.UID()] = Document(obj)
            elif ITask.providedBy(obj) or IProposal.providedBy(obj):
                self._add_task_and_proposal_documents(obj, self.documents)

    def _add_task_and_proposal_documents(self, obj, documents):
        for item in obj.objectValues():
            if IBaseDocument.providedBy(item):
                documents[item.UID()] = Document(item)
            else:
                self._add_task_and_proposal_documents(item, documents)

    def add_content(self, dossier):
        parts = []

        description = safe_unicode(self.obj.Description())

        # strip newlines according to customer requirements:
        # https://4teamwork.atlassian.net/browse/TI-3690?focusedCommentId=66247
        description = description.replace('\n', ' ')

        if description:
            parts.append(
                translate(
                    _(
                        u'sip_content_description',
                        default=u'Description: ${content}',
                        mapping={'content': description},
                    ),
                    context=getRequest(),
                )
            )

        if parts:
            parts.append('')
            dossier.inhalt = ';\n'.join(parts)

    def add_comment(self, dossier):
        parts = []

        archival_value_annotation = ILifeCycle(self.obj).archival_value_annotation
        if archival_value_annotation:
            parts.append(
                translate(
                    _(
                        u'sip_comment_archival_value',
                        default=u'Comment on archival value: ${content}',
                        mapping={'content': archival_value_annotation},
                    ),
                    context=getRequest(),
                )
            )

        parts.append(
            translate(
                _(
                    u'sip_comment_delivery_date',
                    default=u'Delivery date: ${content}',
                    mapping={'content': DateTime().strftime('%Y-%m-%d')},
                ),
                context=getRequest(),
            )
        )
        parts.append('')
        dossier.bemerkung = ';\n'.join(parts)

    def binding(self):
        dossier = arelda.dossierGeverSIP(id=u'_{}'.format(self.obj.UID()))
        dossier.titel = self.obj.Title().decode('utf8')

        dossier.entstehungszeitraum = arelda.historischerZeitraum()
        catalog = getToolByName(self.obj, 'portal_catalog')
        oldest_docs = catalog(
            portal_type=self.document_types,
            path='/'.join(self.obj.getPhysicalPath()),
            sort_on='created',
            sort_order='ascending',
            sort_limit=1)
        if oldest_docs:
            dossier.entstehungszeitraum.von = arelda.historischerZeitpunkt(
                oldest_docs[0].created.asdatetime().date())
        else:
            dossier.entstehungszeitraum.von = NOT_SPECIFIED
        latest_docs = catalog(
            portal_type=self.document_types,
            path='/'.join(self.obj.getPhysicalPath()),
            sort_on='changed',
            sort_order='descending',
            sort_limit=1)
        if oldest_docs:
            dossier.entstehungszeitraum.bis = arelda.historischerZeitpunkt(
                latest_docs[0].changed.date())
        else:
            dossier.entstehungszeitraum.bis = NOT_SPECIFIED

        set_classification_attributes(dossier, self.obj)

        dossier.aktenzeichen = IReferenceNumber(self.obj).get_number()

        dossier_obj = IDossier(self.obj)
        if dossier_obj.start:
            dossier.eroeffnungsdatum = arelda.historischerZeitpunkt(
                dossier_obj.start)
        if dossier_obj.end:
            dossier.abschlussdatum = arelda.historischerZeitpunkt(
                dossier_obj.end)

        dossier.schutzfrist = unicode(ILifeCycle(self.obj).custody_period)

        additional_data = get_additional_data(self.obj)
        if additional_data:
            dossier.zusatzDaten = additional_data

        self.add_content(dossier)
        self.add_comment(dossier)

        for d in self.dossiers.values():
            dossier.dossier.append(d.binding())

        for doc in self.documents.values():
            dossier.dokument.append(doc.binding())

        return dossier

from five import grok
from opengever.document.document import IDocumentSchema
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.interfaces import IContactInformation
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


@grok.subscribe(IDocumentSchema, IObjectAddedEvent)
@grok.subscribe(IDocumentSchema, IObjectModifiedEvent)
def resolve_document_author(document, event):
    if document.document_author:
        info = getUtility(IContactInformation)
        if info.is_user(document.document_author):
            user = info.get_user(document.document_author)
            if user:
                document.document_author = info.describe(
                    user, with_principal=False, with_email=False)

                document.reindexObject(idxs=['sortable_author'])

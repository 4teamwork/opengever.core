from five import grok
from opengever.document.behaviors import  IRelatedDocuments
from opengever.document.document import IDocumentSchema
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent.interfaces import IObjectCopiedEvent


@grok.subscribe(IDocumentSchema, IObjectCopiedEvent)
def set_reference(doc, event):
    """When a document is copied to somewhere the eventhandler store a
    reference to the orignal document in to the new one - the copy"""

    intids = getUtility(IIntIds)
    o_iid = intids.getId(event.original)

    if IRelatedDocuments(doc).relatedItems != None:
        IRelatedDocuments(doc).relatedItems.append(RelationValue(o_iid))
    else:
        IRelatedDocuments(doc).relatedItems = [RelationValue(o_iid)]

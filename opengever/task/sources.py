from opengever.document.document import IBaseDocument
from plone import api
from plone.uuid.interfaces import IUUID
from zope.interface import implementer
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import ISource


@implementer(ISource)
class DocumentsFromTaskSource(object):
    """Builds UIDs of documents either contained in or related to a task.
    """
    def __init__(self, context):
        self.context = context
        task_path = '/'.join(self.context.getPhysicalPath())
        catalog = api.portal.get_tool('portal_catalog')

        related_docs = [rel.to_object for rel in self.context.relatedItems]
        contained_docs = catalog.unrestrictedSearchResults(
            path=task_path,
            object_provides=IBaseDocument.__identifier__,
        )

        self.all_uids = [b.UID for b in contained_docs] + \
                        [IUUID(obj) for obj in related_docs]

    def __contains__(self, value):
        return value in self.all_uids


@implementer(IContextSourceBinder)
class DocumentsFromTaskSourceBinder(object):

    def __call__(self, context):
        return DocumentsFromTaskSource(context)

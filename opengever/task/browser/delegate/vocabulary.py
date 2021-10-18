from opengever.task.task import ITask
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
import AccessControl


@provider(IContextSourceBinder)
def attachable_documents_vocabulary(context):
    terms = []

    user = AccessControl.getSecurityManager().getUser()
    if user == AccessControl.SpecialUsers.nobody:
        return SimpleVocabulary(terms)

    intids = getUtility(IIntIds)

    ids = []

    for doc in context.getFolderContents(
        full_objects=True,
        contentFilter={'portal_type': ['opengever.document.document',
                                       'ftw.mail.mail']}):

        value = str(intids.getId(doc))
        token = doc.UID()
        label = doc.Title()
        terms.append(SimpleVocabulary.createTerm(value, token, label))
        ids.append(value)

    for relation in getattr(context, 'relatedItems', []):
        value = str(relation.to_id)
        token = relation.to_object.UID()
        # check if the task doesn't contain the related document allready
        if value in ids:
            continue
        label = relation.to_object.Title()
        terms.append(SimpleVocabulary.createTerm(value, token, label))

    return SimpleVocabulary(terms)


@implementer(IVocabularyFactory)
class AttachableDocumentsVocabularyFactory(object):

    def __call__(self, context):
        if not ITask.providedBy(context):
            return SimpleVocabulary([])

        return attachable_documents_vocabulary(context)

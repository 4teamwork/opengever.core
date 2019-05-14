from AccessControl import Unauthorized
from opengever.trash import _
from opengever.trash.trash import ITrashed
from plone import api
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent
from zope.event import notify
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implements
from zope.intid.interfaces import IIntIds


class IObjectWillBeRemovedFromTrashEvent(IObjectEvent):
    """Interface of an event which gets fired when removing a document from trash.
    """


class ObjectWillBeRemovedFromTrashEvent(ObjectEvent):
    """The event which gets fired when removing a document from trash.
    """

    implements(IObjectWillBeRemovedFromTrashEvent)


class Remover(object):
    def __init__(self, documents):
        self.documents = documents

    def remove(self):
        self.verify_is_allowed()

        for document in self.documents:
            notify(ObjectWillBeRemovedFromTrashEvent(document))
            api.content.transition(obj=document,
                                   transition=document.remove_transition)

        return True

    def verify_is_allowed(self):
        for document in self.documents:
            if not RemoveConditionsChecker(document).removal_allowed():
                raise RuntimeError('RemoveConditions not satisified')

            if not api.user.get_current().checkPermission(
                    'Remove GEVER content', document):
                raise Unauthorized


class RemoveConditionsChecker(object):

    def __init__(self, document):
        self.document = document
        self.error_msg = []

    def removal_allowed(self):
        self.verify_checked_in()
        self.verify_no_relations()
        self.verify_is_trashed()
        self.verify_is_not_removed()

        if self.error_msg:
            return False
        return True

    def verify_checked_in(self):
        if self.document.is_checked_out():
            self.error_msg.append(
                _(u'msg_document_is_checked_out',
                  default=u'The document is still checked out.'))

    def verify_no_relations(self):
        related_documents = self.document.related_items()
        objs_with_backreferences = self.get_backreferences()
        if related_documents:
            self.error_msg.append(
                _(u'msg_document_has_relations',
                  default=u'The document contains relations.'))

        if objs_with_backreferences:
            links = []
            for obj in objs_with_backreferences:
                type_str = translate(obj.portal_type, 'opengever.core',
                                     context=getRequest())
                links.append(u'<a href={}>{}: {}</a>'.format(
                    obj.absolute_url(), type_str, obj.title))

            self.error_msg.append(
                _(u'msg_document_has_backreferences',
                  default=u'The document is referred by ${links}.',
                  mapping={'links': ', '.join(links)}))

    def verify_is_trashed(self):
        if not ITrashed.providedBy(self.document):
            self.error_msg.append(
                _(u'msg_is_not_trashed',
                  default=u'The document is not trashed.'))

    def verify_is_not_removed(self):
        if self.document.is_removed:
            self.error_msg.append(
                _(u'msg_is_removed',
                  default=u'The document is already removed.'))

    def get_backreferences(self):
        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)

        relations = catalog.findRelations(
            {'to_id': intids.getId(self.document),
             'from_attribute': 'relatedItems'})

        return [rel.from_object for rel in relations if rel.from_object]

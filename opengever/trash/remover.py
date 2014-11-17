from opengever.document.behaviors.related_docs import IRelatedDocuments
from opengever.trash import _
from opengever.trash.trash import ITrashed
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class RemoveConditions(object):

    def __init__(self, document):
        self.document = document
        self.error_msg = []

    def remove_allowed(self):
        self.verify_checked_in()
        self.verify_no_relations()
        self.verify_is_trashed()

        if self.error_msg:
            return False
        return True

    def verify_checked_in(self):
        if self.document.is_checked_out():
            self.error_msg.append(
                _(u'msg_document_is_checked_out',
                  default=u'Document is still checked out'))

    def verify_no_relations(self):
        related_documents = IRelatedDocuments(self.document).relatedItems
        objs_with_backreferences = self.get_backreferences()
        if related_documents:
            self.error_msg.append(
                _(u'msg_document_has_relations',
                  default=u'The documents contains relations'))

        if objs_with_backreferences:
            links = []
            for obj in objs_with_backreferences:
                links.append(u'<a href={}>{}</a>'.format(
                    obj.absolute_url(), obj.title))

            self.error_msg.append(
                _(u'msg_document_has_backreferences',
                  default=u'The documents is reffered by ${links}',
                  mapping={'links': ', '.join(links)}))

    def verify_is_trashed(self):
        if not ITrashed.providedBy(self.document):
            self.error_msg.append(
                _(u'msg_is_not_trashed',
                  default=u'The documents is not trashed.'))

    def get_backreferences(self):
        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        objs = []

        relations = catalog.findRelations(
            {'to_id': intids.getId(self.document),
             'from_attribute': 'relatedItems'})
        for relation in relations:
            objs.append(intids.queryObject(relation.from_id))

        return objs

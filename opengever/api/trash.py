from opengever.api import _
from opengever.api.not_reported_exceptions import BadRequest as NotReportedBadRequest
from opengever.trash.trash import ITrasher
from opengever.trash.trash import TrashError
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.interface import alsoProvides
import plone.protect.interfaces


class TrashPost(Service):
    """Trash an object"""

    def reply(self):

        # Disable CSRF protection
        alsoProvides(self.request,
                     plone.protect.interfaces.IDisableCSRFProtection)

        trasher = ITrasher(self.context)
        try:
            trasher.trash()
        except TrashError as exc:
            if exc.message == 'Already trashed':
                raise NotReportedBadRequest(
                    _(u'msg_already_trashed', default=u'Already trashed'))
            elif exc.message == 'Document checked out':
                raise NotReportedBadRequest(
                    _(u'msg_trash_checked_out_doc',
                      default=u'Cannot trash a checked-out document'))
            elif exc.message == 'The document is locked':
                raise NotReportedBadRequest(
                    _(u'msg_trash_locked_doc', default=u'Cannot trash a locked document'))
            elif exc.message == 'The document has been returned as excerpt':
                raise NotReportedBadRequest(
                    _(u'msg_trash_doc_returned_as_excerpt',
                      default=u'Cannot trash a document that has been returned as excerpt'))
            elif exc.message == 'Not trashable':
                raise BadRequest(
                    _(u'msg_obj_not_trashable', default=u'Object is not trashable'))
            else:
                raise BadRequest(
                    _(u'msg_obj_not_trashable', default=u'Object is not trashable'))

        self.request.response.setStatus(204)
        return super(TrashPost, self).reply()


class UntrashPost(Service):
    """Untrash a document"""

    def reply(self):

        # Disable CSRF protection
        alsoProvides(self.request,
                     plone.protect.interfaces.IDisableCSRFProtection)

        trasher = ITrasher(self.context)
        trasher.untrash()

        self.request.response.setStatus(204)
        return super(UntrashPost, self).reply()

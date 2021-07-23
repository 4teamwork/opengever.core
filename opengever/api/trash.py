from opengever.trash.trash import ITrasher
from opengever.trash.trash import TrashError
from plone.restapi.services import Service
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
            self.request.response.setStatus(400)
            if exc.message == 'Already trashed':
                return {'error': {
                    'type': 'Bad Request',
                    'message': 'Already trashed',
                }}
            elif exc.message == 'Document checked out':
                return {'error': {
                    'type': 'Bad Request',
                    'message': 'Cannot trash a checked-out document',
                }}
            elif exc.message == 'The document is locked':
                return {'error': {
                    'type': 'Bad Request',
                    'message': 'Cannot trash a locked document',
                }}
            elif exc.message == 'The document has been returned as excerpt':
                return {'error': {
                    'type': 'Bad Request',
                    'message': 'Cannot trash a document that has been returned as excerpt',
                }}
            elif exc.message == 'Not trashable':
                return {'error': {
                    'type': 'Bad Request',
                    'message': 'Object is not trashable',
                }}
            else:
                return {'error': {
                    'type': 'Bad Request',
                    'message': 'Object is not trashable',
                }}

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

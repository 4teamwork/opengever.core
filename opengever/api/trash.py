from opengever.trash.trash import ITrashable
from opengever.trash.trash import TrashError
from plone.restapi.services import Service
from zope.interface import alsoProvides

import plone.protect.interfaces


class Trash(Service):
    """Trash a document"""

    def reply(self):

        # Disable CSRF protection
        alsoProvides(self.request,
                     plone.protect.interfaces.IDisableCSRFProtection)

        trasher = ITrashable(self.context)
        try:
            trasher.trash()
        except TrashError as exc:
            if exc.message == 'Already trashed':
                self.request.response.setStatus(400)
                return {'error': {
                    'type': 'Bad Request',
                    'message': 'Already trashed',
                }}
            elif exc.message == 'Document checked out':
                self.request.response.setStatus(400)
                return {'error': {
                    'type': 'Bad Request',
                    'message': 'Can not trash a checked-out document',
                }}

        self.request.response.setStatus(204)
        return super(Trash, self).reply()


class Untrash(Service):
    """Untrash a document"""

    def reply(self):

        # Disable CSRF protection
        alsoProvides(self.request,
                     plone.protect.interfaces.IDisableCSRFProtection)

        trasher = ITrashable(self.context)
        trasher.untrash()

        self.request.response.setStatus(204)
        return super(Untrash, self).reply()

from opengever.base.interfaces import IOpengeverBaseLayer
from plone.locking.interfaces import ILockable
from plone.locking.interfaces import INonStealableLock
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from plone.restapi.services.locking.locking import lock_info
from zope.component import adapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import noLongerProvides


@implementer(IExpandableElement)
@adapter(Interface, IOpengeverBaseLayer)
class Lock(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'lock': {
                '@id': '/'.join((self.context.absolute_url(), '@lock')),
            },
        }
        if expand:
            result['lock'].update(lock_info(self.context) or {})
        return result


class Unlock(Service):
    """Unlock an object"""

    def reply(self):
        lockable = ILockable(self.context)
        if lockable.can_safely_unlock():
            lockable.unlock()

            if INonStealableLock.providedBy(self.context):
                noLongerProvides(self.context, INonStealableLock)

            # Disable CSRF protection
            alsoProvides(self.request, IDisableCSRFProtection)

        return lock_info(self.context)

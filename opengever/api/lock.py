from opengever.base.interfaces import IOpengeverBaseLayer
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services.locking.locking import lock_info
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


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

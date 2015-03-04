from plone.protect.auto import ProtectTransform
from Products.CMFCore.utils import getToolByName
from zope.annotation.attribute import AttributeAnnotations
from zope.component import adapts
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
import logging


LOG = logging.getLogger('opengever.base.protect')


def unprotected_write(obj):
    """Marks ``obj`` so that it does not trigger plone.protect's
    write protection for GET request.
    The flag is not applied recursively.
    """
    if obj is None:
        return obj

    # Unwrap nonpersistent AttributeAnnotations
    if isinstance(obj, AttributeAnnotations):
        unprotected_write(getattr(obj.obj, '__annotations__', None))
        return obj

    LOG.debug('Disable CSRF protection for {}'.format(repr(obj)))
    _get_unprotected_objects().append(obj)
    return obj


def _get_unprotected_objects():
    request = getRequest()
    if request is None:
        # bail out - no request to protect
        return []

    if not hasattr(request, '_unprotected_objects'):
        setattr(request, '_unprotected_objects', [])
    return getattr(request, '_unprotected_objects')


class OGProtectTransform(ProtectTransform):
    adapts(Interface, IBrowserRequest)

    def _registered_objects(self):
        self._global_unprotect()
        objects = super(OGProtectTransform, self)._registered_objects()
        unprotected = _get_unprotected_objects()
        return filter(lambda obj: obj not in unprotected, objects)

    def _global_unprotect(self):
        # portal_memberdata._members cache will be written sometimes.
        unprotected_write(getToolByName(getSite(), 'portal_memberdata')._members)

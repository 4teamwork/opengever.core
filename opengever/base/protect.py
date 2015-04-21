from plone import api
from plone.portlets.constants import CONTEXT_ASSIGNMENT_KEY
from plone.protect.auto import ProtectTransform
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.annotation.attribute import AttributeAnnotations
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
import logging
import re
import transaction


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

    def parseTree(self, result):
        # Rage quit early so that we have no html parsing errors.
        if result in (None, ['']):
            return None

        # Decode content so that we have no problem with latin-9 for example.
        charset_match = re.search(r'charset=(.*)',
                                  self.request.response.getHeader('Content-Type'))
        if charset_match:
            result = map(lambda text: text.decode(charset_match.group(1)).encode('utf-8'),
                         result)

        return super(OGProtectTransform, self).parseTree(result)

    def _get_current_view(self):
        return getattr(self.request, 'steps', [''])[-1]

    def _abort_txn_on_confirm_action_view(self):
        if self._get_current_view() == '@@confirm-action':
            if len(self._registered_objects()) > 0 and \
                    not IDisableCSRFProtection.providedBy(self.request):
                transaction.abort()
                LOG.error(
                    "Error checking for CSRF. Transaction was modified when "
                    "visiting @@confirm-action view. Transaction aborted!)")
                return True

    def _redirect_loop_detected(self):
        # This should never happen: If the current view is @@confirm-action,
        # AND the original_url points to the same view, we assume
        # that there's a redirect loop.
        # If this happened, the _abort_txn_on_confirm_action_view() safeguard
        # above must have failed.
        redirect_url = self.request.form.get('original_url', '')
        return (self._get_current_view() == '@@confirm-action' and
                '@@confirm-action' in redirect_url)

    def _check(self):
        self._abort_txn_on_confirm_action_view()

        if self._redirect_loop_detected():
            LOG.error("Detected redirect loop on @@confirm-action view! "
                      "Breaking loop by redirecting to Plone site.")
            site = api.portal.get()
            return self.request.RESPONSE.redirect(site.absolute_url())

        return super(OGProtectTransform, self)._check()

    def _registered_objects(self):
        self._global_unprotect()
        objects = super(OGProtectTransform, self)._registered_objects()
        unprotected = _get_unprotected_objects()
        return filter(lambda obj: obj not in unprotected, objects)

    def _global_unprotect(self):
        # portal_memberdata._members cache will be written sometimes.
        if IPloneSiteRoot.providedBy(getSite()):
            unprotected_write(getToolByName(getSite(), 'portal_memberdata')._members)

        # always allow writes to context's annotations.
        context = self.request.PARENTS[0]
        if IAnnotatable.providedBy(context):
            annotations = IAnnotations(context)
            unprotected_write(annotations)
            if CONTEXT_ASSIGNMENT_KEY in annotations:
                # also allow writes to context portlet assignments
                unprotected_write(annotations[CONTEXT_ASSIGNMENT_KEY])

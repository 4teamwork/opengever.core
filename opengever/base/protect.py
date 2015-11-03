from BTrees.OOBTree import OOBTree
from copy import copy
from datetime import datetime
from opengever.base.pathfinder import PathFinder
from plone import api
from plone.portlets.constants import CONTEXT_ASSIGNMENT_KEY
from plone.protect.auto import ProtectTransform
from plone.protect.auto import safeWrite
from plone.protect.interfaces import IDisableCSRFProtection
from pprint import pformat
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from ZODB.utils import u64
from zope.annotation.attribute import AttributeAnnotations
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.component.hooks import getSite
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
import gc
import logging
import os
import subprocess
import transaction


LOG = logging.getLogger('opengever.base.protect')


def unprotected_write(obj):
    """Marks ``obj`` so that it does not trigger plone.protect's
    write protection for GET request.
    The flag is not applied recursively.

    This currently delegates most of the work to safeWrite(), but we can't
    quite drop it yet, because:
    - safeWrite() doesn't return the object, which makes it more awkward to use
    - safeWrite() doesn't unwrap non-persistent attribute annotations

    TODO: Possibly move this functionaly upstream (into plone.protect)
    """
    if obj is None:
        return obj

    # Unwrap nonpersistent AttributeAnnotations
    if isinstance(obj, AttributeAnnotations):
        unprotected_write(getattr(obj.obj, '__annotations__', None))
        return obj

    safeWrite(obj)
    return obj


class OGProtectTransform(ProtectTransform):
    adapts(Interface, IBrowserRequest)

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
        should_log_csrf = bool(os.environ.get('CSRF_LOG_ENABLED', True))

        if should_log_csrf:
            # Create a (shallow) copy of _registered_objects and
            # request.__dict__ if we want to log the incident later
            registered_objects_before_check = self._registered_objects()[:]
            request_dict_before_check = copy(self.request.__dict__)

        self._abort_txn_on_confirm_action_view()

        if self._redirect_loop_detected():
            LOG.error("Detected redirect loop on @@confirm-action view! "
                      "Breaking loop by redirecting to Plone site.")
            site = api.portal.get()
            return self.request.RESPONSE.redirect(site.absolute_url())

        is_safe = super(OGProtectTransform, self)._check()

        if not is_safe and should_log_csrf:
            user = api.user.get_current()
            env = {
                'username': user.getUserName() if user else 'unknown-user',
                'url': self.request.getURL(),
                '_registered_objects': registered_objects_before_check,
                'request_dict': request_dict_before_check,
            }
            self._log_csrf_incident(env)

        return is_safe

    def _log_csrf_incident(self, env):
        """Log a CSRF incident to a file.
        """
        max_age = int(os.environ.get('CSRF_LOG_MAX_AGE', 7 * 24 * 60))
        ts = datetime.now()

        log_dir = PathFinder().var_log
        log_filename = 'csrf-{}-{}.log'.format(
            ts.strftime('%Y-%m-%d_%H-%M-%S'), env['username'])
        logfile_path = os.path.join(log_dir, log_filename)

        with open(logfile_path, 'w') as logfile:
            for line in self._build_csrf_report(env):
                log_message = '{}   {}\n'.format(ts.isoformat(), line)
                logfile.write(log_message)

        LOG.warn('CSRF incident has been logged to {}'.format(logfile_path))

        # Remove old incident logs
        subprocess.check_call(
            "find {} -name 'csrf-*.log' -type f -mmin +{} -delete".format(
                log_dir, max_age), shell=True)

    def _build_csrf_report(self, env):
        """Generator that produces a sequence of lines to be logged to a file
        as the CSRF incident report.
        """
        _registered_objects = env['_registered_objects']
        _registered_object_oids = [
            hex(u64(obj._p_oid)) for obj in _registered_objects]
        request_dict = env['request_dict']

        # Drop response from request dict - we know what we're gonna send
        request_dict.pop('response', None)
        request_dict.get('other', {}).pop('RESPONSE', None)

        # Remove basic auth header before logging
        request_dict.pop('_auth', {})
        request_dict.get('_orig_env', {}).pop('HTTP_AUTHORIZATION', None)

        yield 'CSRF incident at {}'.format(env['url'])
        yield '=' * 80
        yield '\n'

        yield 'User:'
        yield '-' * 80
        yield env['username']
        yield '\n'

        yield 'HTTP_REFERER:'
        yield '-' * 80
        yield request_dict.get('environ', {}).get('HTTP_REFERER', '')
        yield '\n'

        yield '_registered_object_oids:'
        yield '-' * 80
        yield pformat(_registered_object_oids)
        yield '\n'

        yield '_registered_objects:'
        yield '-' * 80
        yield pformat(_registered_objects)
        yield '\n'

        yield 'References to registered objects:'
        yield '-' * 80

        for obj in _registered_objects:
            yield "Object: {}".format(obj)
            referrers = gc.get_referrers(obj)
            yield "Referrers:\n{}".format(pformat(referrers))
            yield '\n' * 10

            # Avoid creating reference cycles!
            del referrers

        yield 'Request:\n{}'.format(pformat(request_dict))
        yield '-' * 80

    def _registered_objects(self):
        self._global_unprotect()
        return super(OGProtectTransform, self)._registered_objects()

    def _global_unprotect(self):
        # portal_memberdata._members cache will be written sometimes.
        if IPloneSiteRoot.providedBy(getSite()):
            unprotected_write(getToolByName(getSite(), 'portal_memberdata')._members)

        context = self.getContext()

        # always allow writes to context's annotations.
        if IAnnotatable.providedBy(context):
            annotations = IAnnotations(context)
            unprotected_write(annotations)
            if CONTEXT_ASSIGNMENT_KEY in annotations:
                # also allow writes to context portlet assignments
                unprotected_write(annotations[CONTEXT_ASSIGNMENT_KEY])

        # Allow _dav_writelocks to be initialized
        # see webdav/Lockable.py:64
        if hasattr(context, '_dav_writelocks'):
            unprotected_write(context._dav_writelocks)


class ProtectAwareAttributeAnnotations(AttributeAnnotations):
    """Zope AttributeAnnotations lazily intializes annotations.

    When annotations are initialized on an object we need to unprotect that
    object.
    """

    def __setitem__(self, key, value):
        try:
            annotations = self.obj.__annotations__
        except AttributeError:
            # unprotect new annotations since they will be written
            annotations = unprotected_write(OOBTree())
            # unprotect obj for which we initialize annotations
            unprotected_write(self.obj).__annotations__ = annotations

        annotations[key] = value

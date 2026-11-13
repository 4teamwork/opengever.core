# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from OFS.CopySupport import ResourceLockedError
from opengever.api import _
from opengever.api.not_reported_exceptions import Forbidden as NotReportedForbidden
from opengever.api.utils import get_obj_by_path
from opengever.base.interfaces import IMovabilityChecker
from opengever.bgtasks.model import TASK_STATUS_SUCCEEDED
from opengever.bgtasks.move import paste_clipboard
from opengever.bgtasks.move import TASK_TYPE
from opengever.bgtasks.task import queue_task
from opengever.locking.lock import MOVE_LOCK
from opengever.locking.utils import has_move_lock
from opengever.ogds.base.utils import get_current_admin_unit
from plone import api
from plone.locking.interfaces import ILockable
from plone.locking.interfaces import ITTWLockable
from plone.restapi.deserializer import json_body
from plone.restapi.services.copymove.copymove import Move
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zExceptions import BadRequest
from zExceptions import Forbidden
from zope.interface import alsoProvides
from zope.security import checkPermission
import plone
import six


class Move(Move):
    """Moves existing content objects.
    """

    def get_object(self, key):
        """Copied from the baseclass but uses utils get_obj_by_path
        to fix a traversal bug, when not all path elements are accessible.
        """
        if isinstance(key, six.string_types):
            if key.startswith(self.portal_url):
                # Resolve by URL
                key = key[len(self.portal_url) + 1:]
                if six.PY2:
                    key = key.encode("utf8")
                return get_obj_by_path(self.portal, key)
            elif key.startswith("/"):
                if six.PY2:
                    key = key.encode("utf8")
                    # Resolve by path
                return get_obj_by_path(self.portal, key.lstrip("/"))
            else:
                # Resolve by UID
                brain = self.catalog(UID=key)
                if brain:
                    return brain[0].getObject()

    def validate_source(self, obj, obj_path, target_path, source_paths):
        """Returns the exception for the first rule violated by moving obj
        into the destination, or None if it can be moved.
        """
        if target_path == obj_path or target_path.startswith(obj_path + '/'):
            return NotReportedForbidden(
                _(u'msg_move_destination_inside_source',
                  default=u'An item cannot be moved into itself or one of '
                          u'its subitems.'))

        parts = obj_path.split('/')
        for depth in range(2, len(parts)):
            if '/'.join(parts[:depth]) in source_paths:
                return NotReportedForbidden(
                    _(u'msg_move_item_inside_other_source',
                      default=u'This item is located inside another item '
                              u'that is being moved.'))

        try:
            IMovabilityChecker(obj).validate_movement(self.context)
        except (Forbidden, ResourceLockedError) as exc:
            return exc
        return None

    # Copied from plone.restapi 1.1.0
    # Disables DeleteObjects permission check
    def reply(self):
        # return 401/403 Forbidden if the user has no permission
        if not checkPermission('cmf.AddPortalContent', self.context):
            pm = getToolByName(self.context, 'portal_membership')
            if bool(pm.isAnonymousUser()):
                self.request.response.setStatus(401)
            else:
                self.request.response.setStatus(403)
            return

        data = json_body(self.request)

        source = data.get('source', None)

        if not source:
            raise BadRequest("Property 'source' is required")

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        if not isinstance(source, list):
            source = [source]

        resolved = []
        source_paths = set()
        for item in source:
            obj = self.get_object(item)
            if obj is None:
                continue
            path = '/'.join(obj.getPhysicalPath())
            if path not in source_paths:
                source_paths.add(path)
                resolved.append((item, obj, path))

        if resolved and has_move_lock(self.context):
            raise NotReportedForbidden(
                _(u'msg_move_destination_locked',
                  default=u'Items cannot be moved into a destination that is '
                          u'currently being moved.'))

        target_path = '/'.join(self.context.getPhysicalPath())
        errors = []
        for item, obj, path in resolved:
            error = self.validate_source(obj, path, target_path, source_paths)
            if error is not None:
                errors.append((item, obj, error))

        if errors:
            if len(resolved) == 1:
                raise errors[0][2]
            raise NotReportedForbidden([
                {'field': failed_item,
                 'item_title': safe_unicode(failed_obj.Title()),
                 'error': type(failed_error).__name__,
                 'message': failed_error.message}
                for failed_item, failed_obj, failed_error in errors])

        parents_objs = {}
        for item, obj, path in resolved:
            parent = aq_parent(obj)
            if parent in parents_objs:
                parents_objs[parent].append(obj)
            else:
                parents_objs[parent] = [obj]

        admin_unit = get_current_admin_unit()
        destination_uid = self.context.UID()
        user_id = api.user.get_current().getId()

        status = 200
        results = []
        for parent, objs in parents_objs.items():
            ids = [o.getId() for o in objs]
            clipboard = self.clipboard(parent, ids)

            if admin_unit is None:
                # OGDS not ready yet (e.g. setup/test contexts) - paste
                # inline, under the real request's own security manager.
                paste_clipboard(self.context, clipboard)
                status = 200
            else:
                for obj in objs:
                    if ITTWLockable.providedBy(obj):
                        ILockable(obj).lock(MOVE_LOCK)
                task = queue_task(
                    TASK_TYPE, admin_unit.unit_id,
                    arguments={u'destination_uid': destination_uid,
                               u'clipboard': clipboard,
                               u'user_id': user_id,
                               u'object_uids': [obj.UID() for obj in objs]})
                if task.status == TASK_STATUS_SUCCEEDED:
                    status = 200
                else:
                    status = 202

            for id_ in ids:
                results.append({
                    'source': '{}/{}'.format(
                        parent.absolute_url(), id_),
                    'target': '{}/{}'.format(
                        self.context.absolute_url(), id_),
                })

        self.request.response.setStatus(status)
        return results

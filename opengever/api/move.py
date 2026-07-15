# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from opengever.api.utils import get_obj_by_path
from opengever.base.interfaces import IMovabilityChecker
from opengever.bgtasks.model import TASK_STATUS_SUCCEEDED
from opengever.bgtasks.move import paste_clipboard
from opengever.bgtasks.move import TASK_TYPE
from opengever.bgtasks.task import queue_task
from opengever.locking.lock import MOVE_LOCK
from opengever.ogds.base.utils import get_current_admin_unit
from plone import api
from plone.locking.interfaces import ILockable
from plone.locking.interfaces import ITTWLockable
from plone.restapi.deserializer import json_body
from plone.restapi.services.copymove.copymove import Move
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
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

        parents_objs = {}
        for item in source:
            obj = self.get_object(item)
            if obj is not None:
                # -- Commented out the following block to disable checking for
                # -- delete permission, as in GEVER the user is not allowed to
                # -- delete content.
                # if self.is_moving:
                #     # To be able to safely move the object, the user requires
                #     # permissions on the parent
                #     if not checkPermission('zope2.DeleteObjects', obj) and \
                #        not checkPermission(
                #             'zope2.DeleteObjects', aq_parent(obj)):
                #         self.request.response.setStatus(403)
                #         return
                parent = aq_parent(obj)
                IMovabilityChecker(obj).validate_movement(self.context)
                if parent in parents_objs:
                    parents_objs[parent].append(obj)
                else:
                    parents_objs[parent] = [obj]

        admin_unit = get_current_admin_unit()
        destination_uid = self.context.UID()
        user_id = api.user.get_current().getId()

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

# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from opengever.api.utils import get_obj_by_path
from opengever.base.interfaces import IMovabilityChecker
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

        parents_ids = {}
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
                if parent in parents_ids:
                    parents_ids[parent].append(obj.getId())
                else:
                    parents_ids[parent] = [obj.getId()]

        results = []
        for parent, ids in parents_ids.items():
            result = self.context.manage_pasteObjects(
                cb_copy_data=self.clipboard(parent, ids))
            for res in result:
                results.append({
                    'source': '{}/{}'.format(
                        parent.absolute_url(), res['id']),
                    'target': '{}/{}'.format(
                        self.context.absolute_url(), res['new_id']),
                })
        return results

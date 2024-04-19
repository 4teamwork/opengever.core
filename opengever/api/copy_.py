from AccessControl.SecurityManagement import getSecurityManager
from Acquisition import aq_parent
from opengever.api import _
from opengever.api.not_reported_exceptions import Forbidden as NotReportedForbidden
from opengever.api.utils import get_obj_by_path
from opengever.base import _ as base_mf
from opengever.document.behaviors import IBaseDocument
from opengever.document.handlers import _update_docproperties
from opengever.document.handlers import DISABLE_DOCPROPERTY_UPDATE_FLAG
from opengever.locking.lock import MEETING_EXCERPT_LOCK
from opengever.workspace.utils import is_restricted_workspace_and_guest
from plone import api
from plone.locking.interfaces import ILockable
from plone.restapi.deserializer import json_body
from plone.restapi.services.copymove.copymove import Copy
from zExceptions import Forbidden
from zope.container.interfaces import INameChooser
from zope.i18n import translate
import six


class Copy(Copy):
    def reply(self):
        self.check_preconditions()

        # Do not prepend document titles with 'Copy of'
        # We will do that after renaming ids, but only for the top level object
        self.request['prevent-copyname-on-document-copy'] = True
        # Do not update Doc Properties during copying
        # We will update them after renaming
        self.request[DISABLE_DOCPROPERTY_UPDATE_FLAG] = True

        results = super(Copy, self).reply()
        docs_to_update = set()
        for result in results:
            target_id = result["target"].split("/")[-1]
            obj = self.context[target_id]
            self.recursive_rename_and_fix_creator(obj, docs_to_update)
            result["target"] = obj.absolute_url()

        # Update Doc Properties
        for doc in docs_to_update:
            _update_docproperties(doc, raise_on_error=False)
        return results

    def check_preconditions(self):
        data = json_body(self.request)
        source = data.get("source", [])

        if not isinstance(source, list):
            source = [source]

        for item in source:
            obj = self.get_object(item)
            if not api.user.has_permission("Copy or Move", obj=obj):
                raise NotReportedForbidden(
                    _('copy_object_disallowed',
                      default=u'You are not allowed to copy this object'))

            if is_restricted_workspace_and_guest(obj):
                raise Forbidden()

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

    def recursive_rename_and_fix_creator(self, obj, docs_to_update):
        for subobj in obj.objectValues():
            self.recursive_rename_and_fix_creator(subobj, docs_to_update)

        old_id = obj.getId()
        parent = aq_parent(obj)
        new_id = INameChooser(parent).chooseName(None, obj)

        if new_id != old_id:
            if IBaseDocument.providedBy(obj):
                # Store document for later update of the doc properties.
                # Updating them now would lead to the document not getting stored
                # in bumblebee if its parent is also renamed, because it's path
                # will have changed when the task queue is processed.
                docs_to_update.add(obj)

                # Locks are copied with the objects, which prevents their
                # renaming. For excerpts the copy does not need to be locked
                # so we remove the corresponding locks here.
                lockable = ILockable(obj)
                if lockable.locked():
                    lockable.unlock(MEETING_EXCERPT_LOCK)

            parent.manage_renameObject(old_id, new_id)

        if old_id.startswith('copy_of'):
            obj.title = translate(
                base_mf('copy_of',
                        default='Copy of ${title}',
                        mapping=dict(title=obj.title)),
                context=self.request,
            )
            obj.reindexObject(idxs=['Title', 'sortable_title'])

        # Make sure the user who created the copy is listed as first creator
        # and therefore is the DC Creator of the object.
        userid = getSecurityManager().getUser().getId()
        new_creators = list(obj.creators)
        if userid in obj.creators:
            new_creators.remove(userid)
        new_creators.insert(0, userid)
        obj.creators = tuple(new_creators)
        obj.reindexObject(idxs=['Creator'])

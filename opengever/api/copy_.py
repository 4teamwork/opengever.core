from AccessControl.SecurityManagement import getSecurityManager
from Acquisition import aq_parent
from opengever.api.utils import get_obj_by_path
from opengever.base import _
from opengever.document.behaviors import IBaseDocument
from opengever.document.handlers import DISABLE_DOCPROPERTY_UPDATE_FLAG
from plone.restapi.services.copymove.copymove import Copy
from zope.container.interfaces import INameChooser
from zope.i18n import translate
import six


class Copy(Copy):
    def reply(self):
        # Do not prepend document titles with 'Copy of'
        # We will do that after renaming ids, but only for the top level object
        self.request['prevent-copyname-on-document-copy'] = True
        # Do not update Doc Properties during copying
        # We will update them after renaming
        self.request[DISABLE_DOCPROPERTY_UPDATE_FLAG] = True

        results = super(Copy, self).reply()

        for result in results:
            target_id = result["target"].split("/")[-1]
            obj = self.context[target_id]
            self.recursive_rename_and_fix_creator(obj)
            result["target"] = obj.absolute_url()

        return results

    def get_object(self, key):
        """Copied from the baseclass but uses utils get_obj_by_path
        to fix a traversal bug, when not all path elements are accessible.
        """
        if isinstance(key, six.string_types):
            if key.startswith(self.portal_url):
                # Resolve by URL
                key = key[len(self.portal_url) + 1 :]
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

    def recursive_rename_and_fix_creator(self, obj):
        for subobj in obj.objectValues():
            self.recursive_rename_and_fix_creator(subobj)

        old_id = obj.getId()
        parent = aq_parent(obj)
        new_id = INameChooser(parent).chooseName(None, obj)

        if new_id != old_id:
            if IBaseDocument.providedBy(obj):
                self.request[DISABLE_DOCPROPERTY_UPDATE_FLAG] = False
            else:
                self.request[DISABLE_DOCPROPERTY_UPDATE_FLAG] = True
            parent.manage_renameObject(old_id, new_id)

        if old_id.startswith('copy_of'):
            obj.title = translate(
                _('copy_of', default='Copy of ${title}',
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

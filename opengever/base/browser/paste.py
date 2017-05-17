from opengever.base import _
from opengever.base.clipboard import Clipboard
from plone import api
from Products.Five import BrowserView
from zope.container.interfaces import INameChooser
from zope.interface import alsoProvides
from zope.interface import Interface


class ICopyPasteRequestLayer(Interface):
    """This request layer is activiated during the copy & paste process.
    This allow us to skip automatic renames etc. in the journal.
    """


class PasteClipboardView(BrowserView):
    """A view that pastes objects from our own clipboard to the current context.
    It replaces the default Plone `objectPaste.cpy`. This allows us to use
    our own ID format for pasted objects instead of the default Plone
    (`copy_of_dossier-19`).
    """
    def __call__(self):
        objs = Clipboard(self.request).get_objs()
        if not objs:
            msg = _(u"msg_empty_clipboard",
                    default=u"Can't paste items, the clipboard is emtpy")
            api.portal.show_message(message=msg,
                                    request=self.request, type='error')
            return self.redirect()

        if not self.is_pasting_objects_allowed(objs):
            msg = _(u"msg_pasting_type_not_allowed",
                    default=u"Can't paste items, it's not allowed to add "
                    "objects of this type.")
            api.portal.show_message(
                message=msg, request=self.request, type='error')
            return self.redirect()

        if not self.is_pasting_on_context_allowed():
            msg = _(u"msg_pasting_not_allowed",
                    default=u"Can't paste items, the context does not allow "
                    "pasting items.")
            api.portal.show_message(
                message=msg, request=self.request, type='error')
            return self.redirect()

        self.activate_request_layer()
        self.copy_objects(objs)
        msg = _(u"msg_successfuly_pasted",
                default=u"Objects from clipboard successfully pasted.")
        api.portal.show_message(message=msg, request=self.request, type='info')
        return self.redirect()

    def is_pasting_on_context_allowed(self):
        is_pasting_allowed_view = self.context.restrictedTraverse(
            '@@is_pasting_allowed')

        if not is_pasting_allowed_view:
            # the is_pasting_allowed_view should always be available, but if
            # not we probably cannot paste
            return False
        return is_pasting_allowed_view()

    def is_pasting_objects_allowed(self, objs):
        allowed_content_types = [
            fti.id for fti in self.context.allowedContentTypes()]

        return all(obj.portal_type in allowed_content_types for obj in objs)

    def activate_request_layer(self):
        alsoProvides(self.request, ICopyPasteRequestLayer)

    def copy_objects(self, objs):
        """Copy objects but change id afterwards, generating an id with the
        INameChooser adapter.
        """
        for obj in objs:
            # Using the plone.api does not work because we need the fix from
            # https://github.com/plone/plone.api/commit/79bec69932ca87a4a5cd675db8b0bd9437dddcdf
            # the following code should be replaced with plone.api after the
            # plone update.
            copy_info = self.context.manage_pasteObjects(
                obj.aq_parent.manage_copyObjects(obj.getId()))
            new_id = copy_info[0]['new_id']
            self.rename_object(self.context[new_id])

    def rename_object(self, copy):
        return self._recursive_rename(copy)

    def _recursive_rename(self, obj):
        renamed = api.content.rename(obj, new_id=self.get_new_id(obj))
        for child in renamed.getFolderContents():
            self._recursive_rename(child.getObject())
        return renamed

    def get_new_id(self, obj):
        return INameChooser(self.context).chooseName(None, obj)

    def redirect(self):
        return self.request.RESPONSE.redirect(self.context.absolute_url())

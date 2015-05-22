from five import grok
from opengever.base import _
from opengever.base.clipboard import Clipboard
from plone import api
from zope.container.interfaces import INameChooser
from zope.interface import Interface


class PasteClipboardView(grok.View):
    """A view that pastes objects from our own clipboard to the current context.
    It replaces the default Plone `objectPaste.cpy`. This allows us to use
    our own ID format for pasted objects instead of the default Plone
    (`copy_of_dossier-19`).
    """

    grok.name('paste_clipboard')
    grok.context(Interface)
    grok.require('zope2.View')

    def render(self):
        objs = Clipboard(self.request).get_objs()
        if not objs:
            msg = _(u"msg_empty_clipboard",
                    default=u"Can't paste items, the clipboard is emtpy")
            api.portal.show_message(message=msg,
                                    request=self.request, type='error')
            return self.redirect()

        self.copy_objects(objs)
        msg = _(u"msg_successfuly_pasted",
                default=u"Objects from clipboard successfully pasted.")
        api.portal.show_message(message=msg, request=self.request, type='info')
        return self.redirect()

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

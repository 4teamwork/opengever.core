from five import grok
from opengever.base import _
from plone import api
from zope.container.interfaces import INameChooser
from zope.interface import Interface


class PasteClipboardView(grok.View):
    """A view wich paste object from the cliboard to the current context.
    It replace the default plone `objectPaste.cpy`. This allow us to use our
    own id format, than the default plone format (`copy_of_dossier-19`).
    """

    grok.name('paste_clipboard')
    grok.context(Interface)
    grok.require('zope2.View')

    def render(self):
        clipboard = self.request.get('__cp')
        if not clipboard:
            msg = _(u"msg_empty_cliboard",
                    default=u"Can't paste items, the clipboard is emtpy")
            api.portal.show_message(message=msg,
                                    request=self.request, type='error')
            return self.redirect()

        for item in clipboard.split(':'):
            self.copy_objects(item)

        msg = _(u"msg_successfuly_pasted",
                default=u"Objects from clipboard successfully pasted.")
        api.portal.show_message(message=msg, request=self.request, type='info')
        return self.redirect()

    def copy_objects(self, clipboard):
        """Copy objects but change id afterwards, generating an id with the
        INameChooser adapter.
        """
        result = self.context.manage_pasteObjects(clipboard)
        for item in result:
            new_id = result[0]['new_id']
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

from opengever.base import _
from opengever.base.clipboard import Clipboard
from opengever.document.behaviors import IBaseDocument
from plone import api
from plone.z3cform import layout
from Products.Five.browser import BrowserView


class CopyItemsFormView(layout.FormWrapper):

    def __call__(self):
        objs = self.extract_selected_objects()

        if not objs:
            msg = _(
                u'error_no_items', default=u'You have not selected any Items.')
            api.portal.show_message(
                message=msg, request=self.request, type='error')
            return self.redirect()

        if not self.are_copyable(objs):
            msg = _(u'error_not_copyable',
                    default=u"The item you selected cannot be copied.")
            api.portal.show_message(
                message=msg, request=self.request, type='error')
            return self.redirect()
        if self.is_any_checked_out(objs):
            msg = _(u'error_checked_out_cannot_be_copied',
                    default=u"Checked out documents cannot be copied.")
            api.portal.show_message(
                message=msg, request=self.request, type='error')
            return self.redirect()

        Clipboard(self.request).set_objs(objs)
        msg = _(u'msg_successfuly_copied',
                default=u"Selected objects successfully copied.")
        api.portal.show_message(message=msg, request=self.request, type='info')
        return self.redirect()

    def redirect(self):
        orig_template = self.request.form.get('orig_template')
        url = self.context.absolute_url()
        if orig_template:
            url = orig_template

        return self.request.RESPONSE.redirect(url)

    def extract_selected_objects(self):
        catalog = api.portal.get_tool('portal_catalog')
        paths = self.request.get('paths', [])
        objs = []
        for path in paths:
            brains = catalog({'path': {'query': path, 'depth': 0}})
            assert len(brains) == 1, "Could not find objects at %s" % path
            objs.append(brains[0].getObject())

        return objs

    def is_any_checked_out(self, objs):
        return any(IBaseDocument.providedBy(obj) and obj.is_checked_out() for obj in objs)

    def are_copyable(self, objs):
        return all(obj.cb_isCopyable() for obj in objs)


class CopyItemView(BrowserView):

    def __call__(self):
        if not self.context.cb_isCopyable():
            msg = _(u'error_not_copyable',
                    default=u"The item you selected cannot be copied.")
            msg_type = 'error'
        elif IBaseDocument.providedBy(self.context) and self.context.is_checked_out():
            msg = _(u'error_checked_out_cannot_be_copied',
                    default=u"Checked out documents cannot be copied.")
            msg_type = 'error'
        else:
            Clipboard(self.request).set_objs([self.context])
            msg = _(u'msg_successfuly_copied',
                    default=u"Selected objects successfully copied.")
            msg_type = 'info'
        api.portal.show_message(
            message=msg, request=self.request, type=msg_type)

        return self.request.RESPONSE.redirect(self.context.absolute_url())

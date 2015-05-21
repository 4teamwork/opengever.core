from five import grok
from OFS.CopySupport import cookie_path
from opengever.base import _
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.interfaces import IDexterityContainer
from plone.uuid.interfaces import IUUID
from plone.z3cform import layout
from Products.statusmessages.interfaces import IStatusMessage
import json


class Clipboard(object):

    key = '_clipboard'

    def __init__(self, request):
        self.request = request

    def set_objs(self, objs):
        uuids = [IUUID(obj) for obj in objs]
        value = json.dumps(uuids).encode('base64')
        self.request.RESPONSE.setCookie(
            self.key, value, path=str(cookie_path(self.request)))

    def get_objs(self):
        value = self.request.cookies.get(self.key)
        if value:
            uuids = json.loads(value.decode('base64'))
            return [uuidToObject(uuid) for uuid in uuids]

        return None

    def cookie_path(self):
        # Return a "path" value for use in a cookie that refers
        # to the root of the Zope object space.
        return self.request['BASEPATH1'] or "/"


class CopyItemsFormView(layout.FormWrapper, grok.View):
    grok.context(IDexterityContainer)
    grok.name('copy_items')
    grok.require('zope2.View')

    def __init__(self, context, request):
        layout.FormWrapper.__init__(self, context, request)
        grok.View.__init__(self, context, request)

    def __call__(self):
        objs = self.extract_selected_objects()

        if not objs:
            msg = _(
                u'error_no_items', default=u'You have not selected any Items.')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.redirect()

        if not self.are_copyable(objs):
            msg = _(u'error_not_copyable',
                    default=u"The item you selected cannot be copied.")
            IStatusMessage(
                self.request).addStatusMessage(msg, type='error')
            return self.redirect()

        Clipboard(self.request).set_objs(objs)
        msg = _(u'msg_successfuly_copied',
                default=u"Selected objects successfully copied.")
        IStatusMessage(self.request).addStatusMessage(msg, type='info')

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

    def are_copyable(self, objs):
        return all(obj.cb_isCopyable() for obj in objs)

from plone.z3cform import layout
from five import grok
from plone.dexterity.interfaces import IDexterityContainer
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from opengever.base import _
from Acquisition import aq_inner, aq_parent


class CopyItemsFormView(layout.FormWrapper, grok.View):
    grok.context(IDexterityContainer)
    grok.name('copy_items')
    grok.require('zope2.View')

    def __init__(self, context, request):
        layout.FormWrapper.__init__(self, context, request)
        grok.View.__init__(self, context, request)

    def __call__(self):
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        if 'paths' in self.request.keys():
            paths = self.request.paths
            objlist = []
            cplist = []
            for path in paths:
                # getting Objects with catalog
                obj = portal_catalog(
                    path={'query': path, 'depth': 0})[0].getObject()
                if not obj.cb_isCopyable():
                    msg = _(u'error_not_copyable',
                            default=u"The item you selected cannot be copied")
                    IStatusMessage(
                        self.request).addStatusMessage(msg, type='error')
                    return self.request.response.redirect(
                        self.context.absolute_url())

                objlist.append(obj)
            for objid in objlist:
                cplist.append(
                    aq_parent(aq_inner(objid)).manage_copyObjects(objid.id))
            cpstring = ':'.join(cplist)
            resp = self.request['RESPONSE']
            resp.setCookie(
                '__cp', cpstring, path='%s' % self.cookie_path(self.request))
            self.request['__cp'] = cpstring
        else:
            msg = _(
                u'error_no_items', default=u'You have not selected any Items')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')

        orig_template = self.request.form.get('orig_template')
        if orig_template:
            redir_url = orig_template
        else:
            # orig_template might not be in the request - fall back to context
            redir_url = self.context.absolute_url()
        return self.request.RESPONSE.redirect(redir_url)

    def cookie_path(self, request):
        # Return a "path" value for use in a cookie that refers
        # to the root of the Zope object space.
        return request['BASEPATH1'] or "/"

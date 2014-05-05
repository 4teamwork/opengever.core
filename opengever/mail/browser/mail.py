from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.mail import utils
from ftw.mail.mail import View as ftwView
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize import instance
from zope.component import getUtility


class View(ftwView):

    template = ViewPageTemplateFile('mail_templates/view.pt')

    def __call__(self):
        self.normalizer = getUtility(IIDNormalizer)
        self.mtr = getToolByName(self.context, 'mimetypes_registry')
        return super(View, self).__call__()

    def lookup_mimetype_registry(self, attachment):
        if attachment.get('content-type') == 'application/octet-stream':
            lookup = self.mtr.globFilename(attachment.get('filename'))
        else:
            lookup = self.mtr.lookup(attachment['content-type'])

        if isinstance(lookup, list) or isinstance(lookup, tuple):
            lookup = lookup[0]

        return lookup

    def get_css_class(self, lookup):
        # copied from opengever.base.browser.utils.get_css_class, should be
        # removed when the sprite problematic is solved complety for opengever
        icon_path = lookup.icon_path
        filetype = icon_path[:icon_path.rfind('.')].replace('icon_', '')
        css_class = 'icon-%s' % self.normalizer.normalize(filetype)
        return css_class

    @instance.memoize
    def attachments(self):
        context = aq_inner(self.context)
        attachments = utils.get_attachments(context.msg)
        for attachment in attachments:
            lookup = self.lookup_mimetype_registry(attachment)
            if lookup:
                attachment['class'] = self.get_css_class(lookup)
                attachment['type-name'] = lookup.name()
            else:
                attachment['class'] = ''
                attachment['type-name'] = 'File'

        return attachments

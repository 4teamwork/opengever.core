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

    @instance.memoize
    def attachments(self):
        normalize = getUtility(IIDNormalizer).normalize
        context = aq_inner(self.context)
        attachments = utils.get_attachments(context.msg)
        mtr = getToolByName(context, 'mimetypes_registry')
        for attachment in attachments:
            icon = 'mimetype-plain'
            type_name = 'File'
            if attachment.get('content-type') == 'application/octet-stream':
                lookup = mtr.globFilename(attachment.get('filename'))
            else:
                lookup = mtr.lookup(attachment['content-type'])
            if lookup:
                if isinstance(lookup, list) or isinstance(lookup, tuple):
                    lookup = lookup[0]
                icon = "mimetype-%s" % normalize(lookup.minor())
                type_name = lookup.name()
            attachment['icon'] = icon
            attachment['type-name'] = type_name
        return attachments

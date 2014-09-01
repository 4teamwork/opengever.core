from Acquisition import aq_inner
from five import grok
from ftw.mail import utils
from ftw.mail.mail import IMail
from ftw.mail.mail import View as ftwView
from opengever.base import _ as ogbmf
from opengever.document import _ as ogdmf
from opengever.document.browser.overview import CustomRow
from opengever.document.browser.overview import FieldRow
from opengever.document.browser.overview import Overview
from opengever.mail import _
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize import instance
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility


class PreviewTab(ftwView):

    template = ViewPageTemplateFile('mail_templates/previewtab.pt')

    def __call__(self):
        self.normalizer = getUtility(IIDNormalizer)
        self.mtr = getToolByName(self.context, 'mimetypes_registry')
        return super(PreviewTab, self).__call__()

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


class OverviewTab(Overview):
    grok.context(IMail)

    def get_metadata_config(self):
        return [
            FieldRow('title'),
            FieldRow('IDocumentMetadata.document_date'),
            FieldRow('IDocumentMetadata.document_type'),
            FieldRow('IDocumentMetadata.document_author'),
            CustomRow(self.render_creator_link,
                      label=ogdmf('label_creator', default='creator')),
            FieldRow('IDocumentMetadata.description'),
            FieldRow('IDocumentMetadata.foreign_reference'),
            CustomRow(self.render_file_widget,
                      label=_('label_org_message',
                              default='Original message')),
            FieldRow('IDocumentMetadata.digitally_available'),
            FieldRow('IDocumentMetadata.preserved_as_paper'),
            FieldRow('IDocumentMetadata.receipt_date'),
            FieldRow('IDocumentMetadata.delivery_date'),
            FieldRow('IRelatedDocuments.relatedItems'),
            FieldRow('IClassification.classification'),
            FieldRow('IClassification.privacy_layer'),
            CustomRow(self.render_public_trial_with_edit_link,
                      label=ogbmf('label_public_trial',
                                  default='Public Trial')),
            FieldRow('IClassification.public_trial_statement'),
        ]

    def render_file_widget(self):
        template = ViewPageTemplateFile('mail_templates/file.pt')
        return template(self)

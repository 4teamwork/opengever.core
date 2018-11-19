from Acquisition import aq_inner
from ftw.mail import utils
from ftw.mail.mail import View
from opengever.base import _ as ogbmf
from opengever.document import _ as ogdmf
from opengever.document.browser.overview import CustomRow
from opengever.document.browser.overview import FieldRow
from opengever.document.browser.overview import Overview
from opengever.document.browser.overview import TemplateRow
from opengever.document.browser.overview import WebIntelligentFieldRow
from opengever.mail import _
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize import instance
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.size import byteDisplay


class MailAttachmentsMixin(object):
    """List the attachments of a mailitem."""

    def lookup_mimetype_registry(self, attachment):
        mtr = getToolByName(self.context, 'mimetypes_registry')
        if attachment.get('content-type') == 'application/octet-stream':
            lookup = mtr.globFilename(attachment.get('filename'))
        else:
            lookup = mtr.lookup(attachment['content-type'])

        if lookup and (isinstance(lookup, list) or isinstance(lookup, tuple)):
            lookup = lookup[0]

        return lookup

    def get_attachment_css_class(self, lookup):
        # copied from opengever.base.browser.utils.get_css_class, should be
        # removed when the sprite problematic is solved complety for opengever
        # also duplicated under a different name to sidestep MRO
        icon_path = lookup.icon_path
        filetype = icon_path[:icon_path.rfind('.')].replace('icon_', '')
        normalizer = getUtility(IIDNormalizer)
        css_class = 'icon-{}'.format(normalizer.normalize(filetype))
        return css_class

    @instance.memoize
    def attachments(self):
        context = aq_inner(self.context)
        attachments = utils.get_attachments(context.msg)
        for attachment in attachments:
            lookup = self.lookup_mimetype_registry(attachment)
            if lookup:
                attachment['class'] = self.get_attachment_css_class(lookup)
                attachment['type-name'] = lookup.name()
            else:
                attachment['class'] = ''
                attachment['type-name'] = 'File'

        return attachments


class PreviewTab(MailAttachmentsMixin, View):
    """Render a preview of a mail.

    We need to be mindful of the MRO C3 here as we need the mixin to override
    methods of the ftw.mail.mail.View.
    """

    template = ViewPageTemplateFile('templates/previewtab.pt')


class OverviewTab(MailAttachmentsMixin, Overview):
    """Render an overview of the mailitem."""

    # override template lookup, its realive to this file
    file_template = ViewPageTemplateFile('templates/file.pt')
    attachments_template = ViewPageTemplateFile('templates/attachments.pt')

    def __init__(self, *args, **kwargs):
        super(OverviewTab, self).__init__(*args, **kwargs)
        self.field = self.context.get_file()

    @property
    def file_size(self):
        return byteDisplay(self.field.getSize())

    def get_metadata_config(self):
        rows = [
            FieldRow('title'),
            FieldRow('IDocumentMetadata.document_date'),
            FieldRow('IDocumentMetadata.document_type'),
            FieldRow('IDocumentMetadata.document_author'),
            CustomRow(self.render_creator_link,
                      label=ogdmf('label_creator', default='creator')),
            WebIntelligentFieldRow('IDocumentMetadata.description'),
            FieldRow('IDocumentMetadata.foreign_reference'),
            TemplateRow(self.file_template,
                        label=_('label_org_message', default='Message')),
            TemplateRow(self.attachments_template,
                        label=_('label_documents',
                                default='Attachments')),
            FieldRow('IDocumentMetadata.digitally_available'),
            FieldRow('IDocumentMetadata.preserved_as_paper'),
            FieldRow('IDocumentMetadata.receipt_date'),
            FieldRow('IDocumentMetadata.delivery_date'),
            FieldRow('IRelatedDocuments.relatedItems'),
            FieldRow('IClassification.classification'),
            FieldRow('IClassification.privacy_layer'),
            TemplateRow(self.public_trial_template,
                        label=ogbmf('label_public_trial',
                                    default='Public Trial')),
            FieldRow('IClassification.public_trial_statement'),
        ]

        if api.user.has_permission('cmf.ManagePortal'):
            rows.append(FieldRow('IOGMail.original_message'))
            rows.append(FieldRow('IOGMail.message_source'))

        return rows

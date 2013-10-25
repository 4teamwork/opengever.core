from Products.CMFCore.utils import getToolByName
from opengever.document.document import IDocumentSchema
from opengever.base.viewlets.byline import BylineBase
from opengever.document import _


class DocumentByline(BylineBase):

    def document_date(self):
        return self.to_localized_time(self.context.document_date)

    def responsible(self):
        mt = getToolByName(self.context, 'portal_membership')
        document = IDocumentSchema(self.context)
        return mt.getMemberById(document.responsible)

    def end(self):
        document = IDocumentSchema(self.context)
        return document.end

    def get_items(self):
        return [
            {
                'class': 'document_author',
                'label': _('label_by_author', default='by'),
                'content': self.context.document_author,
                'replace': False
            },
            {
                'class': 'documentModified',
                'label': _('label_start_byline', default='from'),
                'content': self.document_date(),
                'replace': False
            },
            {
                'class': 'sequenceNumber',
                'label': _('label_sequence_number', default='Sequence Number'),
                'content': self.sequence_number(),
                'replace': False
            },
            {
                'class': 'referenceNumber',
                'label': _('label_reference_number',
                           default='Reference Number'),
                'content': self.reference_number(),
                'replace': False
            }
        ]

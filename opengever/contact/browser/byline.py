from opengever.base.viewlets.byline import BylineBase
from opengever.contact import _
from Products.CMFPlone import PloneMessageFactory as PMF


class ContactByline(BylineBase):

    def get_items(self):
        return [
            {'class': 'sequenceNumber',
             'label': _('label_sequence_number', default='Sequence Number'),
             'content': self.context.model.contact_id,
             'replace': False},

            {'class': 'active',
             'label': _('label_active', default='Active'),
             'content': self.active_label(),
             'replace': False}
        ]

    def active_label(self):
        if self.context.model.is_active:
            return PMF('Yes')
        return PMF('No')

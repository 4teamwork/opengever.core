from opengever.base import _ as base_mf
from opengever.base.viewlets.byline import BylineBase
from Products.CMFPlone import PloneMessageFactory as plone_mf


class DispositionByline(BylineBase):

    def get_items(self):
        return [
            {'class': 'document_created',
             'label': base_mf('label_created', default='Created'),
             'content': self.created(),
             'replace': False},
            {'class': 'review_state',
             'label': plone_mf('State', default='State'),
             'content': self.workflow_state(),
             'replace': False},
            {'class': 'last_modified',
             'label': base_mf('label_last_modified', default='Last modified'),
             'content': self.modified(),
             'replace': False},
        ]

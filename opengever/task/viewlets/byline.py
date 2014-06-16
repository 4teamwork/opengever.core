from opengever.base.interfaces import ISequenceNumber, IBaseClientID
from opengever.base.viewlets.byline import BylineBase
from opengever.ogds.base.actor import Actor
from opengever.task import _
from opengever.task.task import ITask
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TaskByline(BylineBase):

    def responsible_link(self):
        return Actor.lookup(
            ITask(self.context).responsible).get_link()

    def sequence_number(self):
        sequence = getUtility(ISequenceNumber)
        return '{} {}'.format(self.get_base_client_id(),
                              sequence.get_number(self.context))

    def get_base_client_id(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IBaseClientID)
        return getattr(proxy, 'client_id')

    def get_items(self):
        return [
            {
                'class': 'responsible',
                'label': _('label_by_author', default='by'),
                'content': self.responsible_link(),
                'replace': True
            },
            {
                'class': 'review_state',
                'label': _('label_workflow_state_byline', default='State'),
                'content': self.workflow_state(),
                'replace': False
            },
            {
                'class': 'last_modified',
                'label': _('label_last_modified', default='last modified'),
                'content': self.modified(),
                'replace': False
            },
            {
                'class': 'document_created',
                'label': _('label_created', default='created'),
                'content': self.created(),
                'replace': False
            },
            {
                'class': 'sequenceNumber',
                'label': _('label_sequence_number', default='Sequence Number'),
                'content': self.sequence_number(),
                'replace': False
            },

        ]

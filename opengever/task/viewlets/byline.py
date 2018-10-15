from opengever.base.interfaces import ISequenceNumber
from opengever.base.viewlets.byline import BylineBase
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.task import _
from opengever.task import is_private_task_feature_enabled
from opengever.task.task import ITask
from Products.CMFPlone import PloneMessageFactory as PMF
from zope.component import getUtility


class TaskByline(BylineBase):

    def get_css_class(self):
        return self.context.get_sql_object().get_css_class()

    def responsible_link(self):
        return Actor.lookup(
            ITask(self.context).responsible).get_link()

    def sequence_number(self):
        sequence = getUtility(ISequenceNumber)
        return u'{} {}'.format(get_current_admin_unit().abbreviation,
                               sequence.get_number(self.context))

    def is_private_label(self):
        return PMF('Yes') if self.context.is_private else PMF('No')

    def get_items(self):
        items = [
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

        if self.context.is_private:
            items.append({
                'class': 'is_private',
                'label': _('label_is_private_byline', default='Private'),
                'content': self.is_private_label(),
                'replace': False
            })

        return items

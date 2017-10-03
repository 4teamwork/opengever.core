from BTrees.OOBTree import OOBTree
from ftw.upgrade import UpgradeStep
from zope.annotation.interfaces import IAnnotations


class FixProposalHistoryEntries(UpgradeStep):
    """Fix proposal history entries.
    """

    def __call__(self):
        query = {'portal_type': 'opengever.meeting.proposal'}
        for proposal in self.objects(query, 'Fix proposal history'):

            history = IAnnotations(proposal).get('object_history', OOBTree())

            for key, value in history.items():
                if value.get('name') and not value.get('history_type'):
                    value.update({'history_type': value.get('name')})

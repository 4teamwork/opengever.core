from Acquisition import aq_base
from ftw.upgrade import UpgradeStep
from opengever.task.localroles import RELATED_ITEMS_KEY
from opengever.task.task import ITask
from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations


class StoreTaskRelatedItemsInAnnotations(UpgradeStep):
    """Store task related items in annotations.
    """

    deferrable = True

    def __call__(self):
        query = {'object_provides': ITask.__identifier__}
        msg = 'Store task related items in annotations.'

        for task in self.objects(query, msg):
            annotations = IAnnotations(task)
            to_ids = [item.to_id for item in getattr(aq_base(task), 'relatedItems', [])]
            if RELATED_ITEMS_KEY not in annotations:
                annotations[RELATED_ITEMS_KEY] = PersistentList(to_ids)

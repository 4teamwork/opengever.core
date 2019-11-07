from ftw.upgrade import UpgradeStep
from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations


ORDER_KEY = 'plone.folder.ordered.order'


def safe_utf8(to_utf8):
    if isinstance(to_utf8, unicode):
        to_utf8 = to_utf8.encode('utf-8')
    return to_utf8


class FixTodoAndTodolistOrderingObjectIdType(UpgradeStep):
    """Fix todo and todolist ordering object id type.

    The id is persisted in an object's parent so we query for all types that
    may contain todo and todolist.
    """
    def __call__(self):
        for obj in self.objects(
                {'portal_type': ['opengever.workspace.todolist',
                                 'opengever.workspace.workspace']},
                'Fix todo and todolist ordering id.'):

            self.ensure_ordering_object_ids_are_utf8(obj)

    def ensure_ordering_object_ids_are_utf8(self, obj):
        annotations = IAnnotations(obj)
        if ORDER_KEY not in annotations:
            return

        fixed_ordering = PersistentList(
            safe_utf8(item_id) for item_id in annotations[ORDER_KEY])
        annotations[ORDER_KEY] = fixed_ordering

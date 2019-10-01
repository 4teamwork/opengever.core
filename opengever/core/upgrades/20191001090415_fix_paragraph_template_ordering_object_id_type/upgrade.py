from ftw.upgrade import UpgradeStep
from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations


ORDER_KEY = 'plone.folder.ordered.order'


def safe_ascii(as_ascii):
    if isinstance(as_ascii, unicode):
        as_ascii = as_ascii.encode('ascii')
    return as_ascii


class FixParagraphTemplateOrderingObjectIdType(UpgradeStep):
    """Fix paragraph template ordering object id type.
    """
    def __call__(self):
        for template in self.objects(
                {'portal_type': ['opengever.meeting.meetingtemplate']},
                'Fix paragraph template ordering id in meeeting template'):

            self.ensure_ordering_object_ids_are_ascii(template)

    def ensure_ordering_object_ids_are_ascii(self, template):
        annotations = IAnnotations(template)
        if ORDER_KEY not in annotations:
            return

        fixed_ordering = PersistentList(
            safe_ascii(item_id) for item_id in annotations[ORDER_KEY])
        annotations[ORDER_KEY] = fixed_ordering

from opengever.base.viewlets.byline import BylineBase
from opengever.tasktemplates import _
from zope.i18n import translate


class TaskTemplateFolderByline(BylineBase):
    """Specific DocumentByLine, for the TasktTemplateFolders"""

    def sequence_type(self):
        return translate(
            self.context.sequence_type_label, context=self.request)

    def get_items(self):
        items = super(TaskTemplateFolderByline, self).get_items()
        items.append(
            {'class': 'sequence_type',
             'label': _('label_sequence_type', default='Type'),
             'content': self.sequence_type(),
             'replace': False})

        return items

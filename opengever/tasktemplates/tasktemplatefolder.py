from opengever.tasktemplates.content.templatefoldersschema import sequence_types
from plone.dexterity.content import Container


class TaskTemplateFolder(Container):

    @property
    def sequence_type_label(self):
        return sequence_types.by_value[self.sequence_type].title

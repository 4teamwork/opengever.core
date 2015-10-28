from five import grok
from opengever.meeting.committee import Committee
from opengever.meeting.committee import ICommittee
from opengever.meeting.form import ModelProxyAddForm
from opengever.meeting.form import ModelProxyEditForm
from plone.directives import dexterity
from z3c.form import field
from z3c.form.interfaces import HIDDEN_MODE


class AddForm(ModelProxyAddForm, dexterity.AddForm):

    grok.name('opengever.meeting.committee')
    content_type = Committee
    fields = field.Fields(Committee.model_schema)


class EditForm(ModelProxyEditForm, dexterity.EditForm):

    grok.context(ICommittee)
    fields = field.Fields(Committee.model_schema, ignoreContext=True)
    content_type = Committee

    def updateWidgets(self):
        if not self.context.is_group_editable():
            self.fields['group_id'].mode = HIDDEN_MODE

        super(EditForm, self).updateWidgets()

from five import grok
from opengever.meeting.committee import Committee
from opengever.meeting.committee import ICommittee
from opengever.meeting.form import MeetingModelAddForm
from opengever.meeting.form import MeetingModelEditForm
from plone.directives import dexterity
from z3c.form import field


class AddForm(MeetingModelAddForm, dexterity.AddForm):

    grok.name('opengever.meeting.committee')
    content_type = Committee
    fields = field.Fields(Committee.model_schema)


class EditForm(MeetingModelEditForm, dexterity.EditForm):

    grok.context(ICommittee)
    fields = field.Fields(Committee.model_schema, ignoreContext=True)
    content_type = Committee

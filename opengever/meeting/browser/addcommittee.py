from five import grok
from opengever.meeting.committee import Committee
from opengever.meeting.form import MeetingModelAddForm
from plone.directives import dexterity
from z3c.form import field


class AddForm(MeetingModelAddForm, dexterity.AddForm):

    grok.name('opengever.meeting.committee')
    content_type = Committee
    fields = field.Fields(Committee.model_schema)

from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.meeting import _
from opengever.meeting.form import ModelAddForm
from opengever.meeting.model import Membership
from plone.directives import form
from zope import schema


class IMembershipModel(form.Schema):
    """Membership model schema interface."""

    form.widget(date_from=DatePickerFieldWidget)
    date_from = schema.Date(
        title=_(u"label_date_from", default=u"Start date"),
        required=True)

    form.widget(date_to=DatePickerFieldWidget)
    date_to = schema.Date(
        title=_(u"label_date_to", default=u"End date"),
        required=True)

    member = schema.Choice(
        title=_('label_member', default=u'Member'),
        source='opengever.meeting.MemberVocabulary',
        required=True)

    role = schema.TextLine(
        title=_(u"label_role", default=u"Role"),
        max_length=256,
        required=False)


class AddMembership(ModelAddForm):

    schema = IMembershipModel
    model_class = Membership

    label = _('Add Membership', default=u'Add Membership')

    def create(self, data):
        data['committee'] = self.context.load_model()
        return super(AddMembership, self).create(data)

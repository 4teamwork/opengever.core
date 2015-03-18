from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.meeting import _
from opengever.meeting.form import ModelAddForm
from opengever.meeting.model import Membership
from plone.directives import form
from z3c.form.interfaces import ActionExecutionError
from zope import schema
from zope.interface import Invalid


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

    def validate(self, data):
        query = Membership.query.overlapping(
            data['date_from'], data['date_to'])
        query = query.filter_by(committee=data['committee'])
        query = query.filter_by(member=data['member'])

        overlapping_membership = query.first()
        if overlapping_membership:
            date_from = overlapping_membership.format_date_from()
            date_to = overlapping_membership.format_date_to()

            msg = _("Can't add membership, it overlaps an existing membership "
                    "from ${date_from} to ${date_to}",
                    mapping=dict(date_from=date_from, date_to=date_to))
            raise(ActionExecutionError(Invalid(msg)))

    def create(self, data):
        data['committee'] = self.context.load_model()
        return super(AddMembership, self).create(data)

    def nextURL(self):
        return super(AddMembership, self).nextURL() + '#memberships'

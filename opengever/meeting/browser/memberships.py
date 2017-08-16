from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.meeting import _
from opengever.meeting.browser.members import MemberView
from opengever.meeting.browser.views import RemoveModelView
from opengever.base.browser.modelforms import ModelAddForm
from opengever.base.browser.modelforms import ModelEditForm
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
        overlapping = Membership.query.fetch_overlapping(
            data['date_from'], data['date_to'],
            data['member'], data['committee'])

        if overlapping:
            msg = _("Can't add membership, it overlaps an existing membership "
                    "from ${date_from} to ${date_to}.",
                    mapping=dict(date_from=overlapping.format_date_from(),
                                 date_to=overlapping.format_date_to()))

            raise(ActionExecutionError(Invalid(msg)))

    def create(self, data):
        data['committee'] = self.context.load_model()
        return super(AddMembership, self).create(data)

    def nextURL(self):
        return super(AddMembership, self).nextURL() + '#memberships'

    def cancelURL(self):
        return self.nextURL()


class EditMembership(ModelEditForm):

    label = _('label_edit_membership', default=u'Edit Membership')

    schema = IMembershipModel

    def __init__(self, context, request):
        super(EditMembership, self).__init__(context, request, context.model)

    def validate(self, data):
        overlapping = Membership.query.fetch_overlapping(
            data.get('date_from'), data.get('date_to'),
            data.get('member'), self.model.committee,
            ignore_id=self.model.membership_id)

        if overlapping:
            msg = _("Can't change membership, it overlaps an existing membership "
                    "from ${date_from} to ${date_to}.",
                    mapping=dict(date_from=overlapping.format_date_from(),
                                 date_to=overlapping.format_date_to()))

            raise(ActionExecutionError(Invalid(msg)))

    def nextURL(self):
        return MemberView.url_for(self.context.parent.parent,
                                  self.model.member)


class RemoveMembership(RemoveModelView):

    def __init__(self, context, request):
        super(RemoveMembership, self).__init__(context, request, context.model)

    @property
    def success_message(self):
        return _('msg_membership_deleted',
                 default=u'The membership was deleted successfully.')

    def nextURL(self):
        return MemberView.url_for(self.context.parent.parent,
                                  self.model.member)

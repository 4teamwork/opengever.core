from five import grok
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.meeting import _
from opengever.meeting.browser.members import MemberView
from opengever.meeting.browser.views import RemoveModelView
from opengever.meeting.form import ModelAddForm
from opengever.meeting.form import ModelEditForm
from opengever.meeting.model import Membership
from plone.directives import form
from Products.Five.browser import BrowserView
from z3c.form import field
from z3c.form.interfaces import ActionExecutionError
from z3c.form.interfaces import INPUT_MODE
from zExceptions import NotFound
from zope import schema
from zope.interface import implements
from zope.interface import Interface
from zope.interface import Invalid
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView


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
                    "from ${date_from} to ${date_to}",
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

    fields = field.Fields(IMembershipModel)
    fields['date_to'].widgetFactory[INPUT_MODE] = DatePickerFieldWidget
    fields['date_from'].widgetFactory[INPUT_MODE] = DatePickerFieldWidget

    def validate(self, data):
        overlapping = Membership.query.fetch_overlapping(
            data.get('date_from'), data.get('date_to'),
            data.get('member'), self.model.committee,
            ignore_id=self.model.membership_id)

        if overlapping:
            msg = _("Can't change membership, it overlaps an existing membership "
                    "from ${date_from} to ${date_to}",
                    mapping=dict(date_from=overlapping.format_date_from(),
                                 date_to=overlapping.format_date_to()))

            raise(ActionExecutionError(Invalid(msg)))

    def nextURL(self):
        return MemberView.url_for(self.context, self.model.member)


class RemoveMembership(RemoveModelView):
    implements(IBrowserView, IPublishTraverse)

    @property
    def success_message(self):
        return _('msg_membership_deleted',
                 default=u'The membership was deleted successfully')

    def nextURL(self):
        return MemberView.url_for(self.context, self.model.member)


class MembershipTraverser(grok.View):

    implements(IPublishTraverse)
    grok.context(Interface)
    grok.name('membership')

    @classmethod
    def url_for(cls, context):
        return "{}/{}".format(
            context.absolute_url(), cls.__view_name__)

    def render(self):
        """This view is never rendered directly.
        This method ist still needed to make grok checks happy, every grokked
        view must have an associated template or 'render' method.
        """
        pass

    def publishTraverse(self, request, name):
        try:
            membership_id = int(name)
        except ValueError:
            raise NotFound

        membership = Membership.query.get(membership_id)
        if membership is None:
            raise NotFound

        return MembershipView(self.context, self.request, membership)


class MembershipView(BrowserView):
    implements(IBrowserView, IPublishTraverse)

    is_model_view = True
    is_model_edit_view = False

    mapped_actions = {
        'edit': EditMembership,
        'remove': RemoveMembership,
    }

    @classmethod
    def url_for(cls, context, membership):
        return "{}/membership/{}".format(
            context.absolute_url(), membership.membership_id)

    def __init__(self, context, request, membership):
        super(MembershipView, self).__init__(context, request)
        self.model = membership

    def publishTraverse(self, request, name):
        if name in self.mapped_actions:
            view_class = self.mapped_actions.get(name)
            return view_class(self.context, self.request, self.model)
        raise NotFound

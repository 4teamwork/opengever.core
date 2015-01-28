from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.base.model import create_session
from opengever.meeting import _
from opengever.meeting.model import Membership
from plone.autoform.form import AutoExtensibleForm
from plone.directives import form
from z3c.form.form import AddForm
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


class AddMembership(AutoExtensibleForm, AddForm):

    ignoreContext = True
    schema = IMembershipModel

    def __init__(self, context, request):
        super(AddMembership, self).__init__(context, request)
        self._created_object = None

    def create(self, data):
        committee = self.context.load_model()
        return Membership(committee=committee, **data)

    def add(self, obj):
        session = create_session()
        session.add(obj)
        session.flush()  # required to create an autoincremented id
        self._created_object = obj

    def nextURL(self):
        return self.context.absolute_url()

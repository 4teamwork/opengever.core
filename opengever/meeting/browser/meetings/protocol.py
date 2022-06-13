from ftw.datepicker.widget import DatePickerFieldWidget
from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.base.schema import UTCDatetime
from opengever.meeting import _
from opengever.meeting.command import ProtocolOperations
from opengever.meeting.vocabulary import get_committee_member_vocabulary
from opengever.ogds.base.sources import AllUsersSourceBinder
from plone.autoform import directives as form
from plone.supermodel import model
from Products.Five.browser import BrowserView
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.interface import Invalid
from zope.interface import invariant


class IMeetingMetadata(model.Schema):
    """Schema interface for meeting metadata."""

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        required=True)

    presidency = schema.Choice(
        title=_('label_presidency', default=u'Presidency'),
        source=get_committee_member_vocabulary,
        required=False)

    form.widget('secretary', KeywordFieldWidget, async=True)
    form.order_after(secretary='other_participants')
    secretary = schema.Choice(
        title=_('label_secretary', default=u'Secretary'),
        source=AllUsersSourceBinder(),
        required=False,
    )

    form.widget(participants=CheckBoxFieldWidget)
    participants = schema.List(
        title=_('label_participants', default='Participants'),
        value_type=schema.Choice(
            source=get_committee_member_vocabulary,
        ),
        required=False,
    )

    other_participants = schema.Text(
        title=_(u"label_other_participants", default=u"Other Participants"),
        required=False)

    protocol_start_page_number = schema.Int(
        title=_(u"label_protocol_start_page_number",
                default=u"Protocol start-page"),
        required=False
    )

    location = schema.TextLine(
        title=_(u"label_location", default=u"Location"),
        max_length=256,
        required=False)

    form.widget('start', DatePickerFieldWidget)
    start = UTCDatetime(
        title=_('label_start', default=u"Start"),
        required=True)

    form.widget('end', DatePickerFieldWidget)
    end = UTCDatetime(
        title=_('label_end', default=u"End"),
        required=False)

    @invariant
    def validate_start_end(data):
        if data.end is not None:
            if data.start >= data.end:
                raise Invalid(
                    _(u'Start date must be before end date.'))


class DownloadProtocolJson(BrowserView):

    operations = ProtocolOperations()

    def __init__(self, context, request):
        super(DownloadProtocolJson, self).__init__(context, request)
        self.model = context.model

    def __call__(self):
        response = self.request.response
        response.setHeader('X-Theme-Disabled', 'True')
        response.setHeader('Content-Type', 'application/json')
        response.setHeader("Content-Disposition",
                           'attachment; filename="{}"'.format('protocol.json'))

        return self.get_protocol_json(pretty=True)

    def get_protocol_json(self, pretty=False):
        return self.operations.get_meeting_data(
            self.model).as_json(pretty=pretty)

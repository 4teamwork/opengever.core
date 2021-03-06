from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.ogds.base.sources import ActualWorkspaceMembersSourceBinder
from opengever.workspace import _
from opengever.workspace.interfaces import IWorkspaceMeeting
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implements
from zope.interface import provider
from opengever.base.schema import UTCDatetime
from ftw.datepicker.widget import DatePickerFieldWidget


@provider(IFormFieldProvider)
class IWorkspaceMeetingSchema(model.Schema):

    model.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=[
            u'responsible',
            u'start',
            u'end',
            u'location',
            u'videoconferencing_url',
            ],
        )

    form.widget('responsible', KeywordFieldWidget, async=True)
    form.order_after(responsible='IOpenGeverBase.description')
    responsible = schema.Choice(
        title=_('label_organizer', default='Organizer'),
        source=ActualWorkspaceMembersSourceBinder(),
        required=True)

    form.widget('start', DatePickerFieldWidget)
    form.order_after(start='responsible')
    start = schema.Datetime(
        title=_(u'label_start', default='Start'),
        required=True)

    form.widget('end', DatePickerFieldWidget)
    form.order_after(end='start')
    end = schema.Datetime(
        title=_(u'label_end', default='End'),
        required=False)

    form.order_after(location='end')
    location = schema.TextLine(
        title=_(u'label_location', default=u'Location'),
        required=False)

    form.order_after(videoconferencing_url='location')
    videoconferencing_url = schema.TextLine(
        title=_(u'label_video_call_link', default=u'Video Call Link'),
        required=False)


class WorkspaceMeeting(Container):
    implements(IWorkspaceMeeting)

from opengever.meeting import _
from opengever.meeting import templates
from opengever.meeting.browser.meetings.meetinglist import MeetingList
from opengever.meeting.command import MIME_DOCX
from opengever.meeting.form import ModelProxyEditForm
from opengever.meeting.model import Meeting
from opengever.meeting.model import Member
from opengever.meeting.protocol import PreProtocol
from opengever.meeting.protocol import PreProtocolData
from opengever.meeting.sablon import Sablon
from opengever.meeting.vocabulary import get_committee_member_vocabulary
from plone import api
from plone.autoform.form import AutoExtensibleForm
from plone.directives import form
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.form import EditForm
from zope import schema


class IGenerateExcerpt(form.Schema):
    """Schema interface for participants of a meeting."""

    some_example_export_setting = schema.Bool(
        title=u'Example export setting',
        required=False)


class GenerateExcerpt(AutoExtensibleForm, EditForm):

    ignoreContext = True
    schema = IGenerateExcerpt

    template = ViewPageTemplateFile('templates/excerpt.pt')

    def __init__(self, context, request, model):
        super(GenerateExcerpt, self).__init__(context, request)
        self.model = model

    def get_pre_protocols(self):
        for agenda_item in self.model.agenda_items:
            if not agenda_item.is_paragraph:
                yield PreProtocol(agenda_item)

    @button.buttonAndHandler(_('Save', default=u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if not errors:
            pre_protocols_to_include = []
            for pre_protocol in self.get_pre_protocols():
                if pre_protocol.name in self.request:
                    pre_protocols_to_include.append(pre_protocol)

            sablon = Sablon(templates.path('protocol_template.docx'))
            sablon.process(PreProtocolData(
                self.model, pre_protocols_to_include).as_json())

            assert sablon.is_processed_successfully(), sablon.stderr
            filename = self.model.get_pre_protocol_filename().encode('utf-8')
            response = self.request.response
            response.setHeader('X-Theme-Disabled', 'True')
            response.setHeader('Content-Type', MIME_DOCX)
            response.setHeader("Content-Disposition",
                               "attachment; filename='{}'".format(filename))
            return sablon.file_data

    @button.buttonAndHandler(_('Cancel', default=u'Cancel'), name='cancel')
    def handleCancel(self, action):
        return self.redirect_to_meetinglist()

    def redirect_to_meetinglist(self):
        return self.request.RESPONSE.redirect(
            MeetingList.url_for(self.context, self.model))

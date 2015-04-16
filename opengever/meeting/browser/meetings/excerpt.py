from opengever.meeting import _
from opengever.meeting.browser.meetings.meetinglist import MeetingList
from opengever.meeting.command import MIME_DOCX
from opengever.meeting.protocol import ExcerptProtocolData
from opengever.meeting.protocol import PreProtocol
from opengever.meeting.sablon import Sablon
from opengever.meeting.sources import all_open_dossiers_source
from plone.autoform.form import AutoExtensibleForm
from plone.directives import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form.form import EditForm
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.interface import Invalid
from zope.interface import invariant


class IGenerateExcerpt(form.Schema):
    """Schema interface with configuration options for excerpt generation.
    """

    dossier = RelationChoice(
        title=_(u'label_accept_select_dossier',
                default=u'Target dossier'),
        description=_(u'help_accept_select_dossier',
                      default=u'Select the target dossier where the '
                               'excerpts should be created.'),
        required=True,

        source=all_open_dossiers_source)

    include_initial_position = schema.Bool(
        title=_(u'Include initial position'),
        required=True, default=True)

    include_legal_basis = schema.Bool(
        title=_(u'Include legal basis'),
        required=True, default=False)

    include_considerations = schema.Bool(
        title=_(u'Include considerations'),
        required=True, default=False)

    include_proposed_action = schema.Bool(
        title=_(u'Include proposed action'),
        required=True, default=False)

    include_discussion = schema.Bool(
        title=_(u'Include discussion'),
        required=True, default=False)

    include_decision = schema.Bool(
        title=_(u'Include decision'),
        required=True, default=True)

    @invariant
    def validate_at_least_one_selected(data):
        """Validate that at least one field is selected."""

        if not (data.include_initial_position or
                data.include_legal_basis or
                data.include_considerations or
                data.include_proposed_action or
                data.include_discussion or
                data.include_decision):
            raise Invalid(
                _(u'Please select at least one field for the excerpt.'))


class GenerateExcerpt(AutoExtensibleForm, EditForm):

    ignoreContext = True
    schema = IGenerateExcerpt

    template = ViewPageTemplateFile('templates/excerpt.pt')

    def __init__(self, context, request, model):
        super(GenerateExcerpt, self).__init__(context, request)
        self.model = model
        self._excerpt_data = None

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

            self._excerpt_data = ExcerptProtocolData(
                self.model, pre_protocols_to_include,
                include_initial_position=data['include_initial_position'],
                include_legal_basis=data['include_legal_basis'],
                include_considerations=data['include_considerations'],
                include_proposed_action=data['include_proposed_action'],
                include_discussion=data['include_discussion'],
                include_decision=data['include_decision'])

    @button.buttonAndHandler(_('Cancel', default=u'Cancel'), name='cancel')
    def handleCancel(self, action):
        return self.redirect_to_meetinglist()

    def redirect_to_meetinglist(self):
        return self.request.RESPONSE.redirect(
            MeetingList.url_for(self.context, self.model))

    def render(self):
        if self._excerpt_data:
            sablon = Sablon(self.model.get_excerpt_template())
            sablon.process(self._excerpt_data.as_json())

            assert sablon.is_processed_successfully(), sablon.stderr
            filename = self.model.get_pre_protocol_filename().encode('utf-8')
            response = self.request.response
            response.setHeader('X-Theme-Disabled', 'True')
            response.setHeader('Content-Type', MIME_DOCX)
            response.setHeader("Content-Disposition",
                               'attachment; filename="{}"'.format(filename))
            return sablon.file_data

        else:
            return super(GenerateExcerpt, self).render()

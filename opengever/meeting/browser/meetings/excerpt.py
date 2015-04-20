from opengever.meeting import _
from opengever.meeting.browser.meetings.meetinglist import MeetingList
from opengever.meeting.command import CreateGeneratedDocumentCommand
from opengever.meeting.command import ManualExcerptOperations
from opengever.meeting.sources import all_open_dossiers_source
from plone.autoform.form import AutoExtensibleForm
from plone.directives import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form.form import EditForm
from z3c.form.interfaces import ActionExecutionError
from z3c.form.interfaces import IDataConverter
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.interface import Invalid
from zope.interface import invariant


class IGenerateExcerpt(form.Schema):
    """Schema interface with configuration options for excerpt generation.
    """

    dossier = RelationChoice(
        title=_(u'label_select_dossier',
                default=u'Target dossier'),
        description=_(u'help_select_dossier',
                      default=u'Select the target dossier where the '
                              'excerpts should be created.'),
        required=True,
        source=all_open_dossiers_source)

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        required=True,
        )

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

    @classmethod
    def url_for(cls, context, meeting):
        return "{}/generate_excerpt".format(
            MeetingList.url_for(context, meeting))

    def __init__(self, context, request, model):
        super(GenerateExcerpt, self).__init__(context, request)
        self.model = model
        self._excerpt_data = None

    def updateWidgets(self):
        super(GenerateExcerpt, self).updateWidgets()
        self.inject_initial_data()

    def inject_initial_data(self):
        if self.request.method != 'GET':
            return

        initial_filename = self.model.get_excerpt_title()
        widget = self.widgets['title']
        value = IDataConverter(widget).toWidgetValue(initial_filename)
        widget.value = value

    def get_agenda_items(self):
        for agenda_item in self.model.agenda_items:
            if not agenda_item.is_paragraph:
                yield agenda_item

    @button.buttonAndHandler(_('Save', default=u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            return

        agenda_items_to_include = []
        for agenda_item in self.get_agenda_items():
            if agenda_item.name in self.request:
                agenda_items_to_include.append(agenda_item)

        if not agenda_items_to_include:
            raise(ActionExecutionError(
                Invalid(_(u"Please select at least one agenda item."))))

        operations = ManualExcerptOperations(
            agenda_items_to_include, data['title'],
            include_initial_position=data['include_initial_position'],
            include_legal_basis=data['include_legal_basis'],
            include_considerations=data['include_considerations'],
            include_proposed_action=data['include_proposed_action'],
            include_discussion=data['include_discussion'],
            include_decision=data['include_decision'])
        command = CreateGeneratedDocumentCommand(
            data['dossier'], self.model, operations)
        command.execute()
        command.show_message()
        return self.redirect_to_meetinglist()

    @button.buttonAndHandler(_('Cancel', default=u'Cancel'), name='cancel')
    def handleCancel(self, action):
        return self.redirect_to_meetinglist()

    def redirect_to_meetinglist(self):
        return self.request.RESPONSE.redirect(
            MeetingList.url_for(self.context, self.model))

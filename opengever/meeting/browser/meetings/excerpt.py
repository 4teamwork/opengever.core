from opengever.meeting import _
from opengever.meeting.command import CreateGeneratedDocumentCommand
from opengever.meeting.command import ManualExcerptOperations
from opengever.meeting.sources import all_open_dossiers_source
from plone.autoform.form import AutoExtensibleForm
from plone.supermodel import model
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form.form import EditForm
from z3c.form.interfaces import ActionExecutionError
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.interface import Invalid
from zope.interface import invariant


class IGenerateExcerpt(model.Schema):
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

    include_publish_in = schema.Bool(
        title=_(u'Include "publish in"'),
        required=True, default=False)

    include_disclose_to = schema.Bool(
        title=_(u'Include "disclose to"'),
        required=True, default=False)

    include_copy_for_attention = schema.Bool(
        title=_(u'Include copy for attention'),
        required=True, default=False)

    @invariant
    def validate_at_least_one_selected(data):
        """Validate that at least one field is selected."""

        if not (data.include_initial_position or
                data.include_legal_basis or
                data.include_considerations or
                data.include_proposed_action or
                data.include_discussion or
                data.include_decision or
                data.include_publish_in or
                data.include_disclose_to or
                data.include_copy_for_attention):
            raise Invalid(
                _(u'Please select at least one field for the excerpt.'))


class GenerateExcerpt(AutoExtensibleForm, EditForm):

    ignoreContext = True
    allow_prefill_from_GET_request = True  # XXX
    schema = IGenerateExcerpt

    template = ViewPageTemplateFile('templates/excerpt.pt')

    def __init__(self, context, request):
        super(GenerateExcerpt, self).__init__(context, request)
        self.model = self.context.model
        self._excerpt_data = None

    def update(self):
        self.inject_initial_data()
        super(GenerateExcerpt, self).update()

    def inject_initial_data(self):
        if self.request.method != 'GET':
            return

        initial_filename = self.model.get_excerpt_title()
        self.request['form.widgets.title'] = initial_filename

        dossier = self.model.get_dossier()
        self.request['form.widgets.dossier'] = ['/'.join(dossier.getPhysicalPath())]

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
            include_decision=data['include_decision'],
            include_publish_in=data['include_publish_in'],
            include_disclose_to=data['include_disclose_to'],
            include_copy_for_attention=data['include_copy_for_attention'])
        command = CreateGeneratedDocumentCommand(
            data['dossier'], self.model, operations)
        command.execute()
        command.show_message()
        return self.redirect_to_meeting()

    @button.buttonAndHandler(_('label_cancel', default=u'Cancel'), name='cancel')
    def handleCancel(self, action):
        return self.redirect_to_meeting()

    def redirect_to_meeting(self):
        return self.request.RESPONSE.redirect(self.model.get_url())

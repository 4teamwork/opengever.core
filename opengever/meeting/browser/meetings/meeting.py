from ftw.datepicker.widget import DatePickerFieldWidget
from ftw.table import helper
from opengever.base.browser.helper import get_css_class
from opengever.base.browser.wizard import BaseWizardStepForm
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.base.form import WizzardWrappedAddForm
from opengever.base.handlebars import prepare_handlebars_template
from opengever.base.helper import title_helper
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.base.schema import TableChoice
from opengever.base.schema import UTCDatetime
from opengever.meeting import _
from opengever.meeting.browser.meetings.agendaitem_list import GenerateAgendaItemList
from opengever.meeting.browser.meetings.agendaitem_list import UpdateAgendaItemList
from opengever.meeting.browser.meetings.transitions import MeetingTransitionController
from opengever.meeting.browser.protocol import MergeDocxProtocol
from opengever.meeting.model import Meeting
from opengever.meeting.model.membership import Membership
from opengever.meeting.proposal import ISubmittedProposal
from operator import itemgetter
from path import Path
from plone import api
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.dexterity.i18n import MessageFactory as pd_mf
from plone.supermodel import model
from plone.z3cform.layout import FormWrapper
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.schema.interfaces import IVocabularyFactory
import json


@provider(IContextAwareDefaultFactory)
def default_title(context):
    return context.Title().decode('utf-8')


class IMeetingModel(model.Schema):
    """Meeting model schema interface."""

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        defaultFactory=default_title,
        required=True)

    meeting_template = TableChoice(
        title=_(u'label_meeting_template', default=u'Meeting Template'),
        description=_(
            u'help_meeting_template',
            default=u'Template containing the predifined paragraphs'),
        vocabulary='opengever.meeting.MeetingTemplateVocabulary',
        columns=(
            {'column': 'title',
             'column_title': _(u'label_title', default=u'Title'),
             'sort_index': 'sortable_title',
             'transform': title_helper},
            {'column': 'Creator',
             'column_title': _(u'label_creator', default=u'Creator'),
             'sort_index': 'document_author'},
            {'column': 'modified',
             'column_title': _(u'label_modified', default=u'Modified'),
             'transform': helper.readable_date}),
        required=False,
    )

    committee = schema.Choice(
        title=_('label_committee', default=u'Committee'),
        source='opengever.meeting.CommitteeVocabulary',
        required=True)

    location = schema.TextLine(
        title=_(u"label_location", default=u"Location"),
        max_length=256,
        required=False)

    start = UTCDatetime(
        title=_('label_start', default=u"Start"),
        required=True)

    end = UTCDatetime(
        title=_('label_end', default=u"End"),
        required=False)


ADD_MEETING_STEPS = (
    ('add-meeting', _(u'Add Meeting')),
    ('add-meeting-dossier', _(u'Add Dossier for Meeting'))
)

TEMPLATES_DIR = Path(__file__).joinpath('..', 'templates').abspath()


def get_dm_key(committee_oguid=None):
    """Return the key used to store meeting-data in the wizard-storage."""
    committee_oguid = committee_oguid or get_committee_oguid()
    return 'create_meeting:{}'.format(committee_oguid)


def get_committee_oguid():
    return Oguid.parse(getRequest().get('committee-oguid'))


class AddMeetingWizardStep(BaseWizardStepForm, Form):
    step_name = 'add-meeting'
    label = _('Add Meeting')
    steps = ADD_MEETING_STEPS

    fields = Fields(IMeetingModel)

    fields['start'].widgetFactory = DatePickerFieldWidget
    fields['end'].widgetFactory = DatePickerFieldWidget

    @buttonAndHandler(_(u'button_continue', default=u'Continue'), name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()
        if errors:
            return

        committee_oguid = Oguid.for_object(self.context)

        dm = getUtility(IWizardDataStorage)
        dm.update(get_dm_key(committee_oguid), data)

        repository_folder = self.context.repository_folder.to_object
        return self.request.RESPONSE.redirect(
            '{}/add-meeting-dossier?committee-oguid={}'.format(
                repository_folder.absolute_url(), committee_oguid))

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def updateWidgets(self):
        super(AddMeetingWizardStep, self).updateWidgets()

        committee_id = self.context.load_model().committee_id
        self.widgets['committee'].mode = HIDDEN_MODE
        self.widgets['committee'].value = (str(committee_id), )

    def nextURL(self):
        return self._created_object.get_url()


class AddMeetingWizardStepView(FormWrapper):

    form = AddMeetingWizardStep


class AddMeetingDossierView(WizzardWrappedAddForm):

    typename = 'opengever.meeting.meetingdossier'

    def _create_form_class(self, parent_form_class, steptitle):
        class WrappedForm(BaseWizardStepForm, parent_form_class):
            step_name = 'add-meeting-dossier'
            step_title = steptitle
            steps = ADD_MEETING_STEPS
            label = _(u'Add Dossier for Meeting')

            passed_data = ['committee-oguid']

            @buttonAndHandler(pd_mf(u'Save'), name='save')
            def handleAdd(self, action):
                # create the dossier
                data, errors = self.extractData()
                if errors:
                    self.status = self.formErrorsMessage
                    return

                committee_oguid = get_committee_oguid()
                dossier = self.create_meeting_dossier(data)
                self.create_meeting(dossier, committee_oguid)

                api.portal.show_message(
                    _(u"The meeting and its dossier were created successfully"),
                    request=self.request,
                    type="info")

                committee = committee_oguid.resolve_object()
                return self.request.RESPONSE.redirect(
                    '{}#meetings'.format(committee.absolute_url()))

            @buttonAndHandler(pd_mf(u'Cancel'), name='cancel')
            def handleCancel(self, action):
                committee_oguid = get_committee_oguid()

                dm = getUtility(IWizardDataStorage)
                dm.drop_data(get_dm_key(committee_oguid))

                committee = committee_oguid.resolve_object()
                return self.request.RESPONSE.redirect(committee.absolute_url())

            def create_meeting_dossier(self, data):
                obj = self.createAndAdd(data)
                if obj is not None:
                    # mark only as finished if we get the new object
                    self._finishedAdd = True
                return obj

            def create_meeting(self, dossier, committee_oguid):
                dm = getUtility(IWizardDataStorage)
                data = dm.get_data(get_dm_key())
                data['dossier_oguid'] = Oguid.for_object(dossier)
                meeting_template_uid = data.pop('meeting_template', None)

                meeting = Meeting(**data)
                if meeting_template_uid is not None:
                    meeting_template = api.content.get(
                        UID=meeting_template_uid)
                    meeting_template.apply(meeting)

                meeting.initialize_participants()
                session = create_session()
                session.add(meeting)
                session.flush()  # required to create an autoincremented id

                dm.drop_data(get_dm_key())
                return meeting

        return WrappedForm

    def __call__(self):
        """Inject meeting title into meeting dossier add form."""

        title_key = 'form.widgets.IOpenGeverBase.title'

        if title_key not in self.request.form:
            dm = getUtility(IWizardDataStorage)
            data = dm.get_data(get_dm_key())
            self.request.set(title_key, data.get('title'))

        return super(AddMeetingDossierView, self).__call__()


class MeetingView(BrowserView):

    template = ViewPageTemplateFile('templates/meeting.pt')

    def __init__(self, context, request):
        super(MeetingView, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        # Enable border to show the zip export action also for
        # committee members. Because the plone_view's `showEditableBorder`
        # checks for `ModifyPortalContent`, we have to enable the border
        # manually.
        self.request.set('enable_border', True)
        return self.template()

    def get_css_class(self, document):
        """Provide CSS classes for icons."""
        return get_css_class(document)

    def transition_url(self, transition):
        return MeetingTransitionController.url_for(
            self.context, self.model, transition.name)

    def unscheduled_proposals(self):
        return self.context.get_unscheduled_proposals()

    def get_protocol_document_label(self):
        if self.model.is_pending():
            return _(u'document_label_pre_protocol', u'Pre-protocol')
        else:
            return _(u'document_label_protocol', u'Protocol')

    def get_protocol_document(self):
        if self.model.protocol_document:
            return IContentListingObject(
                self.model.protocol_document.resolve_document())

    def get_protocol_document_link(self):
        document = self.get_protocol_document()
        return document.render_link(title=self.get_protocol_document_label(),
                                    show_icon=False)

    def get_agendaitem_list_document(self):
        if self.model.agendaitem_list_document:
            return IContentListingObject(
                self.model.agendaitem_list_document.resolve_document())

    def get_agendaitem_list_document_link(self):
        document = self.get_agendaitem_list_document()
        return document.render_link(title=_(u'document_label_agenda_item_list',
                                            default=u'Agenda item list'),
                                    show_icon=False)

    def url_merge_docx_protocol(self, overwrite=False):
        return MergeDocxProtocol.url_for(self.model, overwrite)

    def has_agendaitem_list_document(self):
        return self.model.has_agendaitem_list_document()

    def has_protocol_document(self):
        return self.model.has_protocol_document()

    def url_download_protocol(self):
        if self.has_protocol_document:
            return self.model.protocol_document.get_download_url()

    def was_protocol_manually_edited(self):
        return self.model.was_protocol_manually_edited()

    def will_closing_regenerate_protocol(self):
        """
        The protocol will be generated if it has not been manually edited
        """
        return not self.was_protocol_manually_edited()

    def url_download_agendaitem_list(self):
        if self.has_agendaitem_list_document:
            return self.model.agendaitem_list_document.get_download_url()

    def url_generate_agendaitem_list(self):
        if not self.model.has_agendaitem_list_document():
            return GenerateAgendaItemList.url_for(self.model)
        else:
            return UpdateAgendaItemList.url_for(self.model)

    def render_handlebars_agendaitems_template(self):
        return prepare_handlebars_template(
            TEMPLATES_DIR.joinpath('agendaitems.html'),
            translations=(
                _('label_edit_cancel', default='Cancel'),
                _('label_edit_save', default='Save'),
                _('label_attachments', default='Attachments'),
                _('label_excerpts', default='Excerpts'),
                _('label_toggle_attachments', default='Toggle attachments'),
                _('label_agenda_item_number', default='Agenda item number'),
                _('label_decision_number', default=u'Decision number'),
                _('label_agenda_item_decided', default='Decided'),
                _('action_edit_document', default='Edit with word'),
                _('action_debug_excerpt_docxcompose', default='Debug excerpt docxcompose'),
                _('action_decide', default='Decide'),
                _('action_generate_excerpt', default='Generate excerpt'),
                _('action_rename_agenda_item', default='Rename agenda item'),
                _('action_rename_agenda_paragraph', default='Rename paragraph'),
                _('action_remove_agenda_item', default='Remove agenda item'),
                _('action_remove_agenda_paragraph', default='Remove paragraph'),
                _('action_reopen', default='Reopen agenda item'),
                _('action_return_excerpt', default='Return to proposal'),
                _('help_return_excerpt',
                  default='Return this excerpt the as official answer to the proposal.'),
                _('label_returned_excerpt', default='Returned'),
                _('help_returned_excerpt',
                  default='This excerpt was returned to the dossier'),
                _('action_create_task', default='Create task'),
                _('help_create_task',
                  default='Create a new task the meeting dossier and attach'
                  ' this excerpt.')
            ),
            max_proposal_title_length=ISubmittedProposal['title'].max_length)

    def render_handlebars_navigation_template(self):
        return prepare_handlebars_template(
            TEMPLATES_DIR.joinpath('navigation.html'))

    def render_handlebars_proposals_template(self):
        return prepare_handlebars_template(
            TEMPLATES_DIR.joinpath('proposals.html'),
            translations=(
                _('label_schedule', default='Schedule'),
                _('label_no_proposals', default='No proposals submitted')))

    def json_is_editable(self):
        return json.dumps(self.model.is_editable())

    def json_is_agendalist_editable(self):
        return json.dumps(self.model.is_agendalist_editable())

    @property
    def url_update_agenda_item_order(self):
        return '{}/agenda_items/update_order'.format(self.context.absolute_url())

    @property
    def url_list_agenda_items(self):
        return '{}/agenda_items/list'.format(self.context.absolute_url())

    @property
    def url_schedule_text(self):
        return '{}/agenda_items/schedule_text'.format(self.context.absolute_url())

    @property
    def url_schedule_paragraph(self):
        return '{}/agenda_items/schedule_paragraph'.format(self.context.absolute_url())

    @property
    def url_list_unscheduled_proposals(self):
        return '{}/unscheduled_proposals'.format(self.context.absolute_url())

    @property
    def msg_unexpected_error(self):
        return translate(_('An unexpected error has occurred',
                           default='An unexpected error has occurred'),
                         context=self.request)

    def get_participants(self):
        result = []
        participants = self.model.participants
        presidency = self.model.presidency
        secretary = self.model.secretary

        for membership in Membership.query.for_meeting(self.model):
            item = {'fullname': membership.member.fullname,
                    'email': membership.member.email,
                    'member_id': membership.member.member_id}

            if membership.member in participants:
                item['presence_cssclass'] = 'presence present'
            else:
                item['presence_cssclass'] = 'presence not-present'

            if membership.member == presidency:
                item['role'] = {'name': 'presidency',
                                'label': _(u'meeting_role_presidency',
                                           default=u'Presidency')}
            elif membership.member == secretary:
                item['role'] = {'name': 'secretary',
                                'label': _(u'meeting_role_secretary',
                                           default=u'Secretary')}
            else:
                item['role'] = {'name': '', 'label': ''}

            result.append(item)

        result.sort(key=itemgetter('fullname'))
        return result

    def get_closing_infos(self):
        transition_controller = self.model.workflow.transition_controller
        infos = {'is_closed': False,
                 'close_url': None,
                 'reopen_url': None,
                 'cancel_url': None}

        can_change = api.user.has_permission(
            'Modify portal content',
            obj=self.model.committee.resolve_committee())

        if self.model.is_closed():
            infos['is_closed'] = True
            infos['reopen_url'] = can_change and transition_controller.url_for(
                self.context, self.model, 'closed-held')
        else:
            close_transition = self.get_close_transition()
            if close_transition:
                infos['close_url'] = can_change and transition_controller.url_for(
                    self.context, self.model, close_transition.name)

            cancel_transition = self.get_cancel_transition()
            if cancel_transition:
                infos['cancel_url'] = can_change and transition_controller.url_for(
                    self.context, self.model, cancel_transition.name)

        return infos

    def get_close_transition(self):
        for transition in self.model.workflow.get_transitions(self.model.get_state()):
            if transition.state_to == 'closed' and transition.visible:
                return transition

        return None

    def get_cancel_transition(self):
        for transition in self.model.workflow.get_transitions(self.model.get_state()):
            if transition.state_to == 'cancelled' and transition.visible:
                return transition

        return None

    @property
    def has_many_ad_hoc_agenda_item_templates(self):
        return bool(len(self.ad_hoc_agenda_item_templates) > 1)

    @property
    def ad_hoc_agenda_item_templates(self):
        vocabulary_factory = getUtility(
            IVocabularyFactory,
            name='opengever.meeting.AdHocAgendaItemTemplatesForCommitteeVocabulary')

        committee = self.context.aq_parent
        vocabulary = vocabulary_factory(committee)

        allowed_templates = committee.allowed_ad_hoc_agenda_item_templates
        if allowed_templates is not None and len(allowed_templates):
            templates = [
                term.value
                for term in vocabulary
                if term.token in committee.allowed_ad_hoc_agenda_item_templates
            ]
        else:
            templates = [term.value
                         for term in vocabulary]

        default_template = committee.get_ad_hoc_template()
        return [{
            'title': template.title,
            'modified': template.modified().strftime('%d.%m.%Y'),
            'author': template.getOwner().getId(),
            'selected': template == default_template,
            'value': template.getId(),
        } for template in templates]

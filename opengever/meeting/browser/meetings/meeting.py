from five import grok
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.base.browser.helper import get_css_class
from opengever.base.browser.wizard import BaseWizardStepForm
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.base.form import WizzardWrappedAddForm
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.base.schema import UTCDatetime
from opengever.meeting import _
from opengever.meeting.browser.meetings.transitions import MeetingTransitionController
from opengever.meeting.browser.protocol import GenerateProtocol
from opengever.meeting.browser.protocol import UpdateProtocol
from opengever.meeting.committee import ICommittee
from opengever.meeting.model import Meeting
from opengever.meeting.proposal import ISubmittedProposal
from opengever.repository.interfaces import IRepositoryFolder
from plone import api
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.dexterity.i18n import MessageFactory as pd_mf
from plone.directives import form
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
import json


@provider(IContextAwareDefaultFactory)
def default_title(context):
    return context.Title().decode('utf-8')


class IMeetingModel(form.Schema):
    """Meeting model schema interface."""

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        defaultFactory=default_title,
        required=True)

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

AGENDAITEMS_TEMPLATE = '''
<script id="agendaitemsTemplate" type="text/x-handlebars-template">
  {{#each agendaitems}}
    <tr class="{{css_class}}" data-uid={{id}}>
      {{#if ../agendalist_editable}}<td class="sortable-handle"></td>{{/if}}
      <td class="number">{{number}}</td>
      <td class="title">
        <span>{{{link}}}</span>
        {{#if has_proposal}}
          <ul class="attachements">
            {{#each documents}}
              <li>
                {{{link}}}
              </li>
            {{/each}}
          </ul>
        {{/if}}
        {{#if excerpt}}
          <div class="summary">
            {{{excerpt}}}
          </div>
        {{/if}}
        <div class="edit-box">
          <div class="input-group">
            <input type="text" {{#if has_proposal}}maxlength="%(max_proposal_title_lengt)i"{{/if}} />
            <div class="button-group">
              <input value="%(label_edit_save)s" type="button" class="button edit-save" />
              <input value="%(label_edit_cancel)s" type="button" class="button edit-cancel" />
            </div>
          </div>
        </div>
      </td>
      <td class="toggle-attachements">
        {{#if has_documents}}
          <a class="toggle-attachements-btn"></a>
        {{/if}}
      </td>
      {{#if ../editable}}
      <td class="actions">
        <div class="button-group">
          {{#if ../agendalist_editable}}
              <a href="{{edit_link}}" title="%(label_edit_action)s" class="button edit-agenda-item"></a>
              <a href="{{delete_link}}" title="%(label_delete_action)s" class="button delete-agenda-item"></a>
          {{/if}}
          {{#if decide_link}}
            <a href="{{decide_link}}" title="%(label_decide_action)s" class="button decide-agenda-item"><span></span></a>
          {{/if}}
          {{#if reopen_link}}
            <a href="{{reopen_link}}" title="%(label_reopen_action)s" class="button reopen-agenda-item"><span></span></a>
          {{/if}}
          {{#if revise_link}}
            <a href="{{revise_link}}" title="%(label_revise_action)s" class="button revise-agenda-item"><span></span></a>
          {{/if}}
        </div>
      </td>
      {{/if}}
    </tr>
  {{/each}}
</script>
'''

PROPOSALS_TEMPLATE = '''
<script tal:condition="view/unscheduled_proposals" id="proposalsTemplate" type="text/x-handlebars-template">
  {{#each proposals}}
    <div class="list-group-item submit">
      <a href="{{submitted_proposal_url}}" class="title">{{title}}</a>
      <div class="button-group">
        <a class="button schedule-proposal" href="{{schedule_url}}">%(label_schedule)s</a>
      </div>
    </div>
  {{/each}}
  {{#unless proposals}}
    <span>%(label_no_proposals)s</span>
  {{/unless}}
</script>
'''


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


class AddMeetingWizardStepView(FormWrapper, grok.View):
    grok.context(ICommittee)
    grok.name('add-meeting')
    grok.require('zope2.View')
    form = AddMeetingWizardStep

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)


class AddMeetingDossierView(WizzardWrappedAddForm):
    grok.context(IRepositoryFolder)
    grok.name('add-meeting-dossier')

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
                meeting = self.create_meeting(dossier, committee_oguid)

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
                meeting = Meeting(**data)
                meeting.initialize_participants()
                session = create_session()
                session.add(meeting)
                session.flush()  # required to create an autoincremented id

                dm.drop_data(get_dm_key())
                return meeting

        return WrappedForm

    def __call__(self):
        title_key = 'form.widgets.IOpenGeverBase.title'

        if title_key not in self.request.form:
            dm = getUtility(IWizardDataStorage)
            data = dm.get_data(get_dm_key())

            start_date = api.portal.get_localized_time(datetime=data['start'])
            default_title = _(u'Meeting on ${date}',
                              mapping={'date': start_date})
            self.request.set(title_key, default_title)

        return super(AddMeetingDossierView, self).__call__()


class MeetingView(BrowserView):

    has_model_breadcrumbs = True

    template = ViewPageTemplateFile('templates/meeting.pt')

    def __init__(self, context, request):
        super(MeetingView, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        return self.template()

    def get_css_class(self, document):
        """used for display icons in the view"""
        return get_css_class(document)

    def transition_url(self, transition):
        return MeetingTransitionController.url_for(
            self.context, self.model, transition.name)

    def unscheduled_proposals(self):
        return self.context.get_unscheduled_proposals()

    def get_protocol_document(self):
        if self.model.protocol_document:
            return IContentListingObject(
                self.model.protocol_document.resolve_document())

    def url_protocol(self):
        return self.model.get_url(view='protocol')

    def url_generate_protocol(self):
        if not self.model.has_protocol_document():
            return GenerateProtocol.url_for(self.model)
        else:
            return UpdateProtocol.url_for(self.model)

    def has_protocol_document(self):
        return self.model.has_protocol_document()

    def url_download_protocol(self):
        if self.has_protocol_document:
            return self.model.protocol_document.get_download_url()

    def url_agendaitem_list(self):
        return self.model.get_url(view='agenda_item_list')

    def url_zipexport(self):
        return self.model.get_url(view='zipexport')

    def url_manually_generate_excerpt(self):
        return self.model.get_url(view='generate_excerpt')

    def transitions(self):
        return self.model.get_state().get_transitions()

    def agenda_items(self):
        return self.model.agenda_items

    def manually_generated_excerpts(self):
        docs = [excerpt.resolve_document()
                for excerpt in self.model.excerpt_documents]

        return IContentListing(docs)

    def render_handlebars_agendaitems_template(self):
        label_edit_cancel = translate(_('label_edit_cancel', default='Cancel'), context=self.request)
        label_edit_save = translate(_('label_edit_save', default='Save'), context=self.request)
        label_edit_action = translate(_('label_edit_action', default='edit title'), context=self.request)
        label_delete_action = translate(_('label_delete_action', default='delete this agenda item'), context=self.request)
        label_decide_action = translate(
            _('label_decide_action', default='Decide this agenda item'),
            context=self.request)
        label_reopen_action = translate(
            _('label_reopen_action', default='Reopen this agenda item'),
            context=self.request)
        label_revise_action = translate(
            _('label_revise_action', default='Revise this agenda item'),
            context=self.request)
        return AGENDAITEMS_TEMPLATE % {
            'max_proposal_title_lengt': ISubmittedProposal['title'].max_length,
            'label_edit_cancel': label_edit_cancel,
            'label_edit_save': label_edit_save,
            'label_edit_action': label_edit_action,
            'label_delete_action': label_delete_action,
            'label_decide_action': label_decide_action,
            'label_reopen_action': label_reopen_action,
            'label_revise_action': label_revise_action,
        }

    def render_handlebars_proposals_template(self):
        label_schedule = translate(_('label_schedule', default='Schedule'), context=self.request)
        label_no_proposals = translate(_('label_no_proposals', default='No proposals submitted'), context=self.request)
        return PROPOSALS_TEMPLATE % {'label_schedule': label_schedule,
                                     'label_no_proposals': label_no_proposals}

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

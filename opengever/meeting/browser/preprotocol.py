from five import grok
from opengever.base.source import RepositoryPathSourceBinder
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.meeting import _
from opengever.meeting.command import CreatePreProtocolCommand
from opengever.meeting.model import Meeting
from opengever.repository.repositoryroot import IRepositoryRoot
from plone.directives.form import Schema
from plone.z3cform.layout import FormWrapper
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from z3c.relationfield.schema import RelationChoice
from zExceptions import NotFound
from zope import schema


class IChooseDossierSchema(Schema):

    dossier = RelationChoice(
        title=_(u'label_accept_select_dossier',
                default=u'Target dossier'),
        description=_(u'help_accept_select_dossier',
                      default=u'Select the target dossier where the '
                               'pre-protocol should be created.'),
        required=True,

        source=RepositoryPathSourceBinder(
            object_provides='opengever.dossier.behaviors.dossier.IDossierMarker',
            review_state=DOSSIER_STATES_OPEN,
            navigation_tree_query={
                'object_provides': [
                    'opengever.repository.repositoryroot.IRepositoryRoot',
                    'opengever.repository.repositoryfolder.'
                    'IRepositoryFolderSchema',
                    'opengever.dossier.behaviors.dossier.IDossierMarker',
                    ],
                'review_state': ['repositoryroot-state-active',
                                 'repositoryfolder-state-active'] +
                                 DOSSIER_STATES_OPEN,
                }))

    # hidden field
    meeting_id = schema.Int(required=True)


class ChooseDossierForm(Form):
    fields = Fields(IChooseDossierSchema)
    ignoreContext = True

    def updateWidgets(self):
        super(ChooseDossierForm, self).updateWidgets()

        self.widgets['meeting_id'].mode = HIDDEN_MODE
        if not self.widgets['meeting_id'].value:
            initial_value = self.request.get('meeting_id', None)
            self.widgets['meeting_id'].value = initial_value

    @buttonAndHandler(_(u'button_generate', default=u'Generate'), name='save')
    def handle_generate(self, action):
        data, errors = self.extractData()
        if not errors:
            dossier = data['dossier']
            meeting = Meeting.get(data['meeting_id'])

            if not meeting:
                raise NotFound
            # XXX permission checks on meeting?

            document = CreatePreProtocolCommand(dossier, meeting).execute()
            return self.request.RESPONSE.redirect(document.absolute_url())

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'), name='cancel')
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('')


class GeneratePreProtocol(FormWrapper, grok.View):
    grok.context(IRepositoryRoot)
    grok.name('generate_pre_protocol')
    grok.require('zope2.View')

    form = ChooseDossierForm

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)

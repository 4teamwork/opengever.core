"""This module is part of the accept-task wizard and contains the steps and
views for the method when a user wants to work within an existing dossier and
the task needs to be copied to this dossier (successor task).
"""

from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.base.oguid import Oguid
from opengever.base.source import RepositoryPathSourceBinder
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.task import _
from opengever.task.browser.accept.main import AcceptWizardFormMixin
from opengever.task.browser.accept.utils import accept_forwarding_with_successor
from opengever.task.browser.accept.utils import accept_task_with_successor
from plone import api
from plone.supermodel.model import Schema
from plone.uuid.interfaces import IUUID
from plone.z3cform.layout import FormWrapper
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.validator import SimpleFieldValidator
from z3c.form.validator import WidgetValidatorDiscriminators
from z3c.relationfield.schema import RelationChoice
from zope.component import getUtility
from zope.interface import Invalid


class IChooseDossierSchema(Schema):

    dossier = RelationChoice(
        title=_(u'label_accept_select_dossier',
                default=u'Target dossier'),
        description=_(u'help_accept_select_dossier',
                      default=u'Select the target dossier where you like to '
                      'handle the task.'),
        required=True,

        source=RepositoryPathSourceBinder(
            object_provides='opengever.dossier.behaviors.dossier.'
            'IDossierMarker',
            review_state=DOSSIER_STATES_OPEN,
            navigation_tree_query={
                'object_provides': [
                    'opengever.repository.repositoryroot.IRepositoryRoot',
                    'opengever.repository.repositoryfolder.'
                    'IRepositoryFolderSchema',
                    'opengever.dossier.behaviors.dossier.IDossierMarker',
                    ],
                'review_state': [
                    'repositoryroot-state-active',
                    'repositoryfolder-state-active'
                    ] + DOSSIER_STATES_OPEN,
                }))


class DossierValidator(SimpleFieldValidator):

    def validate(self, value):
        super(DossierValidator, self).validate(value)
        task_addable = False
        for fti in value.allowedContentTypes():
            if fti.id == 'opengever.task.task':
                task_addable = True
                break

        if not task_addable:
            msg = _(u'You cannot add tasks in the selected dossier. Either '
                    u'the dossier is closed or you do not have the '
                    u'privileges.')
            raise Invalid(msg)


WidgetValidatorDiscriminators(DossierValidator,
                              field=IChooseDossierSchema['dossier'])


class ChooseDossierStepForm(AcceptWizardFormMixin, Form):
    fields = Fields(IChooseDossierSchema)
    step_name = 'accept_choose_dossier'

    steps = (
        ('accept_choose_method',
         _(u'step_1', default=u'Step 1')),

        ('accept_choose_dossier',
         _(u'step_2', default=u'Step 2')),
        )

    @buttonAndHandler(_(u'button_save', default=u'Save'),
                      name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()

        if not errors:
            oguid = self.request.get('oguid')
            key = 'accept:%s' % oguid
            dm = getUtility(IWizardDataStorage)
            text = dm.get(key, 'text')

            # forwarding
            if dm.get(key, 'is_forwarding'):
                if dm.get(key, 'is_only_assign'):
                    transition_data = {
                        'text': text,
                        'dossier': IUUID(data['dossier'])}

                    wftool = api.portal.get_tool('portal_workflow')
                    task = wftool.doActionFor(
                        Oguid.parse(oguid).resolve_object(),
                        'forwarding-transition-assign-to-dossier',
                        comment=transition_data['text'], **transition_data)

                    IStatusMessage(self.request).addStatusMessage(
                        _(u'The forwarding is now assigned to the dossier'),
                        'info')
                    self.request.RESPONSE.redirect(
                        '%s/edit' % task.absolute_url())

                else:
                    task = accept_forwarding_with_successor(
                        self.context, oguid, text, dossier=data['dossier'])
                    IStatusMessage(self.request).addStatusMessage(
                        _(u'The forwarding has been stored in the local inbox '
                          u'and the succesor task has been created'), 'info')
                    self.request.RESPONSE.redirect(
                        '%s/edit' % task.absolute_url())

            # task
            else:
                task = accept_task_with_successor(
                    data['dossier'], oguid, text)

                IStatusMessage(self.request).addStatusMessage(
                    _(u'The task has been copied to the selected dossier and '
                      u'accepted.'), 'info')
                self.request.RESPONSE.redirect(task.absolute_url())

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'), name='cancel')
    def handle_cancel(self, action):
        portal_url = getToolByName(self.context, 'portal_url')
        url = '%s/resolve_oguid?oguid=%s' % (
            portal_url(), self.request.get('oguid'))
        return self.request.RESPONSE.redirect(url)


class ChooseDossierStepView(FormWrapper):

    form = ChooseDossierStepForm


class ChooseDosserStepRedirecter(BrowserView):
    """Remote admin units redirects usually to the site root,
    but this step needs to be called on the repository root.

    The remote client does not know the URL to the repository root, so it
    redirects to the site root. This view just redirects to the repository
    root, passing the parameters on.
    """

    def __call__(self):
        root = self.context.restrictedTraverse(
            '@@primary_repository_root').get_primary_repository_root()

        url = '%s/@@accept_choose_dossier?%s' % (
            root.absolute_url(),
            self.request.get('QUERY_STRING'))

        return self.request.RESPONSE.redirect(url)

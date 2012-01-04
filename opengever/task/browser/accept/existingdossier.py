"""This module is part of the accept-task wizard and contains the steps and
views for the method when a user wants to work within an existing dossier and
the task needs to be copied to this dossier (successor task).
"""

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.base.source import RepositoryPathSourceBinder
from opengever.task import _
from opengever.task.browser.accept.main import AcceptWizardFormMixin
from opengever.task.browser.accept.utils import accept_task_with_successor
from plone.directives.form import Schema
from plone.z3cform.layout import FormWrapper
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.interface import Interface


class IChooseDossierSchema(Schema):

    # XXX: validator: dossier should be writeable
    dossier = RelationChoice(
        title=_(u'label_accept_select_dossier',
                default=u'Target dossier'),
        description=_(u'help_accept_select_dossier',
                      default=u'Select the target dossier where you like to '
                      'handle the task.'),
        required=True,

        source=RepositoryPathSourceBinder(
            object_provides='opengever.dossier.behaviors.dossier.' + \
                'IDossierMarker',
            navigation_tree_query={
                'object_provides': [
                    'opengever.repository.repositoryroot.IRepositoryRoot',
                    'opengever.repository.repositoryfolder.' + \
                        'IRepositoryFolderSchema',
                    'opengever.dossier.behaviors.dossier.IDossierMarker',
                    ]}))

    text = schema.Text(
        title=_(u'label_response', default=u'Response'),
        description=_(u'help_accept_task_response',
                      default=u'Enter a answer text which will be shown '
                      u'as response when the task is accepted.'),
        required=False,
        )


class ChooseDossierStepForm(AcceptWizardFormMixin, Form):
    fields = Fields(IChooseDossierSchema)
    step_name = 'accept_choose_dossier'
    passed_data = ['oguid']

    steps = (
        ('accept_choose_method',
         _(u'accept_step_1', default=u'Step 1')),

        ('accept_choose_dossier',
         _(u'accept_step_2', default=u'Step 2')),
        )

    @buttonAndHandler(_(u'button_continue', default=u'Continue'), name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()

        if not errors:
            task = accept_task_with_successor(
                data['dossier'], self.request.get('oguid'), data['text'])
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


class ChooseDossierStepView(FormWrapper, grok.View):
    grok.context(Interface)
    grok.name('accept_choose_dossier')
    grok.require('zope2.View')

    form = ChooseDossierStepForm

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)

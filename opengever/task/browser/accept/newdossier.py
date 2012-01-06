"""This module is part of the accept-task wizard and provides steps views for
the parts of the wizard where the user is able to instantly create a new
dossier where the task is then filed.
"""

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.base.source import RepositoryPathSourceBinder
from opengever.globalindex.interfaces import ITaskQuery
from opengever.repository.interfaces import IRepositoryFolder
from opengever.task import _
from opengever.task.browser.accept.main import AcceptWizardFormMixin
from opengever.task.browser.accept.storage import IAcceptTaskStorageManager
from opengever.task.browser.accept.utils import accept_task_with_successor
from plone.dexterity.i18n import MessageFactory as dexterityMF
from plone.directives.form import Schema
from plone.z3cform.layout import FormWrapper
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.validator import SimpleFieldValidator
from z3c.form.validator import WidgetValidatorDiscriminators
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.interface import Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
import urllib


class AcceptWizardNewDossierFormMixin(AcceptWizardFormMixin):

    steps = (

        ('accept_choose_method',
         _(u'accept_step_1', default=u'Step 1')),

        ('accept_select_repositoryfolder',
         _(u'accept_step_2', default=u'Step 2')),

        ('accept_select_dossier_type',
         _(u'accept_step_3', default=u'Step 3')),

        ('accept_dossier_add_form',
         _(u'accept_step_4', default=u'Step 4')),
        )


# ------------------- SELECT REPOSITORY FOLDER --------------------------

class ISelectRepositoryfolderSchema(Schema):

    repositoryfolder = RelationChoice(
        title=_(u'label_accept_select_repositoryfolder',
                default=u'Repository folder'),
        description=_(u'help_accept_select_repositoryfolder',
                      default=u'Select the repository folder within the '
                      'dossier should be created.'),
        required=True,

        source=RepositoryPathSourceBinder(
            object_provides='opengever.repository.repositoryfolder.' + \
                'IRepositoryFolderSchema',
            navigation_tree_query={
                'object_provides': [
                    'opengever.repository.repositoryroot.IRepositoryRoot',
                    'opengever.repository.repositoryfolder.' + \
                        'IRepositoryFolderSchema',
                    ]
                }))


class RepositoryfolderValidator(SimpleFieldValidator):

    def validate(self, value):
        super(RepositoryfolderValidator, self).validate(value)

        # The user should be able to create a dossier (of any type) in the
        # selected repository folder.
        dossier_behavior = 'opengever.dossier.behaviors.dossier.IDossier'
        dossier_addable = False

        for fti in value.allowedContentTypes():
            if dossier_behavior in getattr(fti, 'behaviors', ()):
                dossier_addable = True
                break

        if not dossier_addable:
            msg = _(u'You cannot add dossiers in the selected repository '
                    u'folder. Either you do not have the privileges or the '
                    u'repository folder contains another repository folder.')
            raise Invalid(msg)

WidgetValidatorDiscriminators(
    RepositoryfolderValidator,
    field=ISelectRepositoryfolderSchema['repositoryfolder'])
grok.global_adapter(RepositoryfolderValidator)



class SelectRepositoryfolderStepForm(AcceptWizardNewDossierFormMixin, Form):
    fields = Fields(ISelectRepositoryfolderSchema)

    step_name = 'accept_select_repositoryfolder'
    passed_data = ['oguid']

    @buttonAndHandler(_(u'button_continue', default=u'Continue'),
                      name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()

        if not errors:
            folder = data['repositoryfolder']
            url = folder.absolute_url()

            url += '/@@accept_select_dossier_type?oguid=%s' % (
                self.request.get('oguid'))
            return self.request.RESPONSE.redirect(url)

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'),
                      name='cancel')
    def handle_cancel(self, action):
        portal_url = getToolByName(self.context, 'portal_url')
        url = '%s/resolve_oguid?oguid=%s' % (
            portal_url(), self.request.get('oguid'))

        IStatusMessage(self.request).addStatusMessage(
            _(u'Accepting task cancelled.'), 'info')

        return self.request.RESPONSE.redirect(url)

    def updateWidgets(self):
        super(SelectRepositoryfolderStepForm, self).updateWidgets()


class SelectRepositoryfolderStepView(FormWrapper, grok.View):
    grok.context(Interface)
    grok.name('accept_select_repositoryfolder')
    grok.require('zope2.View')

    form = SelectRepositoryfolderStepForm

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)


# ------------------- SELECT DOSSIER TYPE --------------------------


@grok.provider(IContextSourceBinder)
def allowed_dossier_types_vocabulary(context):
    dossier_behavior = 'opengever.dossier.behaviors.dossier.IDossier'

    terms = []
    for fti in context.allowedContentTypes():
        if dossier_behavior not in getattr(fti, 'behaviors', ()):
            continue

        title = MessageFactory(fti.i18n_domain)(fti.title)
        terms.append(SimpleTerm(value=fti.id, title=title))

    return SimpleVocabulary(terms)


class ISelectDossierTypeSchema(Schema):

    # XXX hide if only one dossier type is selectable?
    dossier_type = schema.Choice(
        title=_('label_accept_select_dossier_type', default=u'Dossier type'),
        description=_(u'help_accept_select_dossier_type',
                      default=u'Select the type for the new dossier.'),
        source=allowed_dossier_types_vocabulary,
        required=True)


class SelectDossierTypeStepForm(AcceptWizardNewDossierFormMixin, Form):
    fields = Fields(ISelectDossierTypeSchema)
    step_name = 'accept_select_dossier_type'
    passed_data = ['oguid']

    @buttonAndHandler(_(u'button_continue', default=u'Continue'),
                      name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()

        if not errors:
            oguid = self.request.get('oguid')
            dm = getUtility(IAcceptTaskStorageManager)
            dm.update(data, oguid=oguid)

            url = '%s/@@accept_dossier_add_form?oguid=%s&%s' % (
                self.context.absolute_url(),
                oguid,
                urllib.urlencode(data))
            return self.request.RESPONSE.redirect(url)

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'),
                      name='cancel')
    def handle_cancel(self, action):
        portal_url = getToolByName(self.context, 'portal_url')
        url = '%s/resolve_oguid?oguid=%s' % (
            portal_url(), self.request.get('oguid'))

        IStatusMessage(self.request).addStatusMessage(
            _(u'Accepting task cancelled.'), 'info')

        return self.request.RESPONSE.redirect(url)


class SelectDossierTypeStepView(FormWrapper, grok.View):
    grok.context(IRepositoryFolder)
    grok.name('accept_select_dossier_type')
    grok.require('zope2.View')

    form = SelectDossierTypeStepForm

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)



# ------------------- DOSSIER ADD FORM --------------------------


class DossierAddFormView(FormWrapper, grok.View):
    grok.context(IRepositoryFolder)
    grok.name('accept_dossier_add_form')
    grok.require('cmf.AddPortalContent')

    def __init__(self, context, request):
        typename = request.get('dossier_type')

        ttool = getToolByName(context, 'portal_types')
        self.ti = ttool.getTypeInfo(typename)

        FormWrapper.__init__(self, context, request)
        grok.View.__init__(self, context, request)

        # Set portal_type name on newly created form instance
        if self.form_instance is not None and \
                not getattr(self.form_instance, 'portal_type', None):
            self.form_instance.portal_type = self.ti.getId()

    @property
    def form(self):
        if getattr(self, '_form', None) is not None:
            return self._form

        add_view = queryMultiAdapter((self.context, self.request, self.ti),
                                     name=self.ti.factory)
        if add_view is None:
            add_view = queryMultiAdapter((self.context, self.request,
                                          self.ti))

        self._form = self._wrap_form(add_view.form)

        return self._form

    def _wrap_form(self, formclass):
        class WrappedForm(AcceptWizardNewDossierFormMixin, formclass):
            step_name = 'accept_dossier_add_form'
            passed_data = ['oguid', 'dossier_type']

            @buttonAndHandler(dexterityMF('Save'), name='save')
            def handleAdd(self, action):
                # create the dossier
                data, errors = self.extractData()
                if errors:
                    self.status = self.formErrorsMessage
                    return
                obj = self.createAndAdd(data)
                if obj is not None:
                    # mark only as finished if we get the new object
                    self._finishedAdd = True

                # Get a properly aq wrapped object
                dossier = self.context.get(obj.id)

                dm = getUtility(IAcceptTaskStorageManager)
                oguid = self.request.get('oguid')

                # create the successor task, accept the predecessor
                task = accept_task_with_successor(
                    dossier,
                    oguid,
                    dm.get('text', oguid=oguid))

                IStatusMessage(self.request).addStatusMessage(
                    _(u'The new dossier has been created and the task has '
                      u'been copied to the new dossier.'), 'info')

                self.request.RESPONSE.redirect(task.absolute_url())

            @buttonAndHandler(dexterityMF(u'Cancel'), name='cancel')
            def handleCancel(self, action):
                portal_url = getToolByName(self.context, 'portal_url')
                url = '%s/resolve_oguid?oguid=%s' % (
                    portal_url(), self.request.get('oguid'))

                # XXX remove cancelled messages on remote client: the message
                # is never displayed because the user is redirected to the
                # source client.
                IStatusMessage(self.request).addStatusMessage(
                    _(u'Accepting task cancelled.'), 'info')

                return self.request.RESPONSE.redirect(url)

        WrappedForm.__name__ = 'WizardForm: %s' % formclass.__name__
        return WrappedForm

    def __call__(self):
        oguid = self.request.get('oguid')

        query = getUtility(ITaskQuery)
        task = query.get_task_by_oguid(oguid)

        # XXX use DOSSIER title as default title, not TASK title - the
        # globalindex contianing_dossier is missing yet, see:
        # Issue #1253 Darstellung Dossiertitel bei Suchresultaten (Subdossiers, Dokumente, Aufgaben)
        # https://extranet.4teamwork.ch/projects/opengever-kanton-zug/sprint-backlog/1253

        title_key = 'form.widgets.IOpenGeverBase.title'

        if self.request.form.get(title_key, None) is None:
            title = task.title
            if isinstance(title, str):
                title = title.decode('utf-8')
            self.request.set(title_key, title)

        return FormWrapper.__call__(self)

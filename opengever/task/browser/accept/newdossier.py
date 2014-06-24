"""This module is part of the accept-task wizard and provides steps views for
the parts of the wizard where the user is able to instantly create a new
dossier where the task is then filed.
"""

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.base.source import RepositoryPathSourceBinder
from opengever.globalindex.interfaces import ITaskQuery
from opengever.repository.interfaces import IRepositoryFolder
from opengever.task import _
from opengever.task.browser.accept.main import AcceptWizardFormMixin
from opengever.task.browser.accept.utils import \
    accept_forwarding_with_successor
from opengever.task.browser.accept.utils import accept_task_with_successor
from opengever.task.browser.accept.utils import assign_forwarding_to_dossier
from plone.dexterity.i18n import MessageFactory as dexterityMF
from plone.dexterity.i18n import MessageFactory as pd_mf
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

    @property
    def steps(self):
        # Default: 3 steps. But if more than one dossier type is addable on
        # the selected repository folder, display 3 steps and also show the
        # the dossier step selection step.

        if IRepositoryFolder.providedBy(self.context) and \
                len(allowed_dossier_types_vocabulary(self.context)) > 1:
            return (
                ('accept_choose_method',
                 _(u'step_1', default=u'Step 1')),

                ('accept_select_repositoryfolder',
                 _(u'step_2', default=u'Step 2')),

                ('accept_select_dossier_type',
                 _(u'step_3', default=u'Step 3')),

                ('accept_dossier_add_form',
                 _(u'step_4', default=u'Step 4')))

        return (
            ('accept_choose_method',
             _(u'step_1', default=u'Step 1')),

            ('accept_select_repositoryfolder',
             _(u'step_2', default=u'Step 2')),

            ('accept_dossier_add_form',
             _(u'step_3', default=u'Step 3')))


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
            object_provides='opengever.repository.repositoryfolder.'
                'IRepositoryFolderSchema',
            navigation_tree_query={
                'object_provides': [
                    'opengever.repository.repositoryroot.IRepositoryRoot',
                    'opengever.repository.repositoryfolder.'
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

    @buttonAndHandler(_(u'button_continue', default=u'Continue'),
                      name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()

        if not errors:
            folder = data['repositoryfolder']
            url = folder.absolute_url()

            args = '?oguid=%s' % self.request.get('oguid')

            dossier_type_voc = allowed_dossier_types_vocabulary(folder)
            if len(dossier_type_voc) > 1:
                viewname = '@@accept_select_dossier_type'

            else:
                viewname = '@@accept_dossier_add_form'
                args += '&dossier_type=%s' % (
                    dossier_type_voc.by_value.keys()[0])

            url += '/%s%s' % (viewname, args)
            return self.request.RESPONSE.redirect(url)

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'),
                      name='cancel')
    def handle_cancel(self, action):
        portal_url = getToolByName(self.context, 'portal_url')
        url = '%s/resolve_oguid?oguid=%s' % (
            portal_url(), self.request.get('oguid'))
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


class SelectRepositoryfolderStepRedirector(grok.View):
    """Remote orgunit redirects usually to the site root,
    but this step needs to be called on the repository root.

    The remote orgunit does not know the URL to the repository root, so it
    redirects to the site root. This view just redirects to the repository
    root, passing the parameters on.
    """

    grok.context(IPloneSiteRoot)
    grok.name('accept_select_repositoryfolder')
    grok.require('zope2.View')

    def render(self):
        root = self.context.restrictedTraverse(
            '@@primary_repository_root').get_primary_repository_root()

        url = '%s/@@accept_select_repositoryfolder?%s' % (
            root.absolute_url(),
            self.request.get('QUERY_STRING'))

        return self.request.RESPONSE.redirect(url)

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

    dossier_type = schema.Choice(
        title=_('label_accept_select_dossier_type', default=u'Dossier type'),
        description=_(u'help_accept_select_dossier_type',
                      default=u'Select the type for the new dossier.'),
        source=allowed_dossier_types_vocabulary,
        required=True)


class SelectDossierTypeStepForm(AcceptWizardNewDossierFormMixin, Form):
    fields = Fields(ISelectDossierTypeSchema)
    step_name = 'accept_select_dossier_type'

    @buttonAndHandler(_(u'button_continue', default=u'Continue'),
                      name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()

        if not errors:
            oguid = self.request.get('oguid')
            dmkey = 'accept:%s' % oguid
            dm = getUtility(IWizardDataStorage)
            dm.update(dmkey, data)

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
        # This form wraps the dossier add form into the wizard. It is
        # important that the original dossier add form is used, since there
        # may be custom things like hidden widgets in updateWidgets(). There
        # are also several ways how a dexterity add form can be customized.
        # Therefor we just get the original add form from the add-view and
        # wrap it with our wizard stuff. See _wrap_form()

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
        # The original form is passed as `formclass` here and is "extended"
        # with the wizard stuff (different template, passing of values from
        # earlier steps, step configuration etc.). This is done by
        # subclassing the original form and overwriting the buttons, since
        # we need to do our custom stuff instead of the default dossier
        # creation.

        steptitle = pd_mf(u'Add ${name}',
                          mapping={'name': self.ti.Title()})

        class WrappedForm(AcceptWizardNewDossierFormMixin, formclass):
            step_name = 'accept_dossier_add_form'
            passed_data = ['oguid', 'dossier_type']
            step_title = steptitle

            @buttonAndHandler(_(u'button_save', default=u'Save'),
                              name='save')
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

                dm = getUtility(IWizardDataStorage)
                oguid = self.request.get('oguid')
                dmkey = 'accept:%s' % oguid

                # forwarding
                if dm.get(dmkey, 'is_forwarding'):
                    if dm.get(dmkey, 'is_only_assign'):
                        task = assign_forwarding_to_dossier(
                            self.context, oguid, dossier, dm.get(
                                dmkey, 'text'))

                        IStatusMessage(self.request).addStatusMessage(
                            _(u'The forwarding is now assigned to the new '
                              'dossier'),
                            'info')

                        self.request.RESPONSE.redirect(
                            '%s/edit' % task.absolute_url())

                    else:
                        task = accept_forwarding_with_successor(
                            self.context,
                            oguid,
                            dm.get(dmkey, 'text'),
                            dossier=dossier)

                        IStatusMessage(self.request).addStatusMessage(
                            _(u'The forwarding has been stored in the '
                              u'local inbox and the succesor task has been'
                              u' created'), 'info')

                        self.request.RESPONSE.redirect(
                            '%s/edit' % task.absolute_url())

                else:
                    # create the successor task, accept the predecessor
                    task = accept_task_with_successor(
                        dossier,
                        oguid,
                        dm.get(dmkey, 'text'))

                    IStatusMessage(self.request).addStatusMessage(
                        _(u'The new dossier has been created and the task '
                          u'has been copied to the new dossier.'), 'info')

                    self.request.RESPONSE.redirect(task.absolute_url())

            @buttonAndHandler(dexterityMF(u'Cancel'), name='cancel')
            def handleCancel(self, action):
                portal_url = getToolByName(self.context, 'portal_url')
                url = '%s/resolve_oguid?oguid=%s' % (
                    portal_url(), self.request.get('oguid'))
                return self.request.RESPONSE.redirect(url)

        WrappedForm.__name__ = 'WizardForm: %s' % formclass.__name__
        return WrappedForm

    def __call__(self):
        oguid = self.request.get('oguid')

        # The default value for the title of the new dossier should be the
        # title of the remote dossier, which contains the task which is
        # accepted with this wizard.
        title_key = 'form.widgets.IOpenGeverBase.title'

        query = getUtility(ITaskQuery)
        task = query.get_task_by_oguid(oguid)

        if not task.is_forwarding:
            if self.request.form.get(title_key, None) is None:
                title = task.containing_dossier
                if isinstance(title, str):
                    title = title.decode('utf-8')
                self.request.set(title_key, title)

        return FormWrapper.__call__(self)

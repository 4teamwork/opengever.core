from Products.CMFCore.PortalFolder import PortalFolderBase
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from five import grok
from opengever.base.source import RepositoryPathSourceBinder
from opengever.globalindex.interfaces import ITaskQuery
from opengever.ogds.base.utils import get_client_id
from opengever.repository.interfaces import IRepositoryFolder
from opengever.task import _
from opengever.task.task import ITask
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.i18n import MessageFactory as dexterityMF
from plone.dexterity.utils import getAdditionalSchemata
from plone.directives.form import Schema
from plone.directives.form import fieldset
from plone.directives.form import mode
from plone.z3cform.layout import FormWrapper
from z3c.form.browser.radio import RadioFieldWidget
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import INPUT_MODE
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface, alsoProvides
from zope.intid.interfaces import IIntIds
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
import urllib



# ------------------- WIZARD --------------------------


class AcceptWizardFormMixin(object):
    """Mixin class for adding wizard support.
    """

    steps = (

        ('accept_choose_method',
         _(u'accept_step_1', default=u'Step 1')),

        ('...', u'...'),
        )

    label = _(u'title_accept_task', u'Accept task')
    template = ViewPageTemplateFile(
        'templates/wizard_wrappedform.pt')
    ignoreContext = True

    def wizard_steps(self):
        current_reached = False

        for name, label in self.steps:
            classes = ['wizard-step-%s' % name]
            if name == self.step_name:
                current_reached = True
                classes.append('selected')

            elif not current_reached:
                classes.append('visited')

            yield {'name': name,
                   'label': label,
                   'class': ' '.join(classes)}


class AcceptTask(grok.View):
    grok.context(ITask)
    grok.name('accept_task')
    grok.require('cmf.AddPortalContent')

    def render(self):
        url = '@@accept_choose_method'
        return self.request.RESPONSE.redirect(url)


# ------------------- CHOOSE METHOD --------------------------


method_vocabulary = SimpleVocabulary([
                SimpleTerm(value=u'participate',
                           title=_(u'accept_method_participate',
                                   default=u"process in issuer's dossier")),

                SimpleTerm(value=u'existing_dossier',
                           title=_(u'accept_method_existing_dossier',
                                   default=u'file in existing dossier')),

                SimpleTerm(value=u'new_dossier',
                           title=_(u'accept_method_new_dossier',
                                   default=u'file in new dossier'))])


class IChooseMethodSchema(Schema):

    method = schema.Choice(
        title=_('label_accept_choose_method',
                default=u'Accept the task and ...'),
        vocabulary=method_vocabulary,
        required=True)


class ChooseMethodStepForm(AcceptWizardFormMixin, Form):
    fields = Fields(IChooseMethodSchema)
    fields['method'].widgetFactory[INPUT_MODE] = RadioFieldWidget

    step_name = 'accept_choose_method'

    @buttonAndHandler(_(u'button_continue', default=u'Continue'), name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()

        if not errors:
            method = data.get('method')
            if method == 'participate':
                transition = 'task-transition-open-in-progress'
                url = '@@addresponse?form.widgets.transition=%s' % transition
                return self.request.RESPONSE.redirect(url)

            elif method == 'existing_dossier':
                raise NotImplementedError()

            elif method == 'new_dossier':
                # XXX: redirect to target client
                intids = getUtility(IIntIds)
                iid = intids.getId(self.context)
                oguid = '%s:%s' % (get_client_id(), str(iid))

                portal_url = getToolByName(self.context, 'portal_url')
                # XXX: should "ordnungssystem" really be hardcode?
                url = '@@accept_select_repositoryfolder?' + \
                    'form.widgets.oguid=%s' % oguid
                return self.request.RESPONSE.redirect('/'.join((
                            portal_url(), 'ordnungssystem', url)))

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')


class ChooseMethodStepView(FormWrapper, grok.View):
    grok.context(ITask)
    grok.name('accept_choose_method')
    grok.require('cmf.AddPortalContent')

    form = ChooseMethodStepForm

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)

    __call__ = FormWrapper.__call__


# ################### NEW DOSSIER ##########################


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

    oguid = schema.TextLine()

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


class SelectRepositoryfolderStepForm(AcceptWizardNewDossierFormMixin, Form):
    fields = Fields(ISelectRepositoryfolderSchema)

    step_name = 'accept_select_repositoryfolder'

    @buttonAndHandler(_(u'button_continue', default=u'Continue'), name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()

        # XXX validate if repositoryfolder can contain a dossier
        if not errors:
            folder = data['repositoryfolder']
            url = folder.absolute_url()

            url += '/@@accept_select_dossier_type?form.widgets.oguid=%s' % data['oguid']
            return self.request.RESPONSE.redirect(url)

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        data, errors = self.extractData()
        portal_url = getToolByName(self.context, 'portal_url')
        url = '%s/resolve_oguid?oguid=%s' % (portal_url(), data['oguid'])
        return self.request.RESPONSE.redirect(url)

    def updateWidgets(self):
        super(SelectRepositoryfolderStepForm, self).updateWidgets()
        self.widgets['oguid'].mode = HIDDEN_MODE


class SelectRepositoryfolderStepView(FormWrapper, grok.View):
    grok.context(Interface)
    grok.name('accept_select_repositoryfolder')
    grok.require('zope2.View')

    form = SelectRepositoryfolderStepForm

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)

    __call__ = FormWrapper.__call__


# ------------------- SELECT DOSSIER TYPE --------------------------


@grok.provider(IContextSourceBinder)
def allowed_dossier_types_vocabulary(context):
    dossier_behavior = 'opengever.dossier.behaviors.dossier.IDossier'

    terms = []
    for fti in PortalFolderBase.allowedContentTypes(context):
        if dossier_behavior not in getattr(fti, 'behaviors', ()):
            continue

        title = MessageFactory(fti.i18n_domain)(fti.title)
        terms.append(SimpleTerm(value=fti.id, title=title))

    return SimpleVocabulary(terms)


class ISelectDossierTypeSchema(Schema):

    oguid = schema.TextLine()

    dossier_type = schema.Choice(
        title=_('label_accept_select_dossier_type', default=u'Dossier type'),
        description=_(u'help_accept_select_dossier_type',
                      default=u'Select the type for the new dossier.'),
        source=allowed_dossier_types_vocabulary,
        required=True)


class SelectDossierTypeStepForm(AcceptWizardNewDossierFormMixin, Form):
    fields = Fields(ISelectDossierTypeSchema)
    step_name = 'accept_select_dossier_type'

    @buttonAndHandler(_(u'button_continue', default=u'Continue'), name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()

        if not errors:
            url = '%s/@@accept_dossier_add_form?%s' % (
                self.context.absolute_url(),
                urllib.urlencode(data))
            return self.request.RESPONSE.redirect(url)

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        data, errors = self.extractData()
        portal_url = getToolByName(self.context, 'portal_url')
        url = '%s/resolve_oguid?oguid=%s' % (
            portal_url(), data['oguid'])
        return self.request.RESPONSE.redirect(url)

    def updateWidgets(self):
        super(SelectDossierTypeStepForm, self).updateWidgets()
        self.widgets['oguid'].mode = HIDDEN_MODE


class SelectDossierTypeStepView(FormWrapper, grok.View):
    grok.context(IRepositoryFolder)
    grok.name('accept_select_dossier_type')
    grok.require('zope2.View')

    form = SelectDossierTypeStepForm


    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)

    __call__ = FormWrapper.__call__


# ------------------- DOSSIER ADD FORM --------------------------


class IDossierAddFormAdditionalSchema(Schema):

    fieldset(
        u'common',
        fields=[
            u'oguid',
            ])

    mode(oguid='hidden')
    oguid = schema.TextLine()

alsoProvides(IDossierAddFormAdditionalSchema, IFormFieldProvider)


class DossierAddFormView(FormWrapper, grok.View):
    grok.context(IRepositoryFolder)
    grok.name('accept_dossier_add_form')
    # XXX improve permissions
    grok.require('zope2.View')

    def __init__(self, context, request):
        typename = request.form.get('dossier_type')
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

            @property
            def additionalSchemata(self):
                yield IDossierAddFormAdditionalSchema
                for schema in getAdditionalSchemata(
                    portal_type=self.portal_type):
                    yield schema

        WrappedForm.__name__ = 'WizardForm: %s' % formclass.__name__
        return WrappedForm

    def update(self):
        oguid = self.request.get('oguid')
        self.request.set('form.widgets.IDossierAddFormAdditionalSchema.oguid',
                         oguid)

        query = getUtility(ITaskQuery)
        task = query.get_task_by_oguid(oguid)

        # XXX use DOSSIER title as default title, not TASK title - the
        # globalindex contianing_dossier is missing yet, see:
        # Issue #1253 Darstellung Dossiertitel bei Suchresultaten (Subdossiers, Dokumente, Aufgaben)
        # https://extranet.4teamwork.ch/projects/opengever-kanton-zug/sprint-backlog/1253
        self.request.set('form.widgets.IOpenGeverBase.title', task.title)

        FormWrapper.update(self)

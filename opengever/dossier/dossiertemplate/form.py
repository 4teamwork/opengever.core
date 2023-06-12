from AccessControl import getSecurityManager
from ftw.keywordwidget.widget import KeywordWidget
from ftw.table import helper
from opengever.base.behaviors.base import IOpenGeverBase
from opengever.base.browser.wizard import BaseWizardStepForm
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.base.form import WizzardWrappedAddForm
from opengever.base.monkey.patches.cmf_catalog_aware import DeactivatedCatalogIndexing
from opengever.base.oguid import Oguid
from opengever.base.schema import TableChoice
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.command import CreateDocumentFromTemplateCommand
from opengever.dossier.command import CreateDossierFromTemplateCommand
from opengever.dossier.dossiertemplate import is_create_dossier_from_template_available
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplate
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateSchema
from opengever.dossier.dossiertemplate.behaviors import IRestrictAddableDossierTemplates
from opengever.dossier.dossiertemplate.dossiertemplate import BEHAVIOR_INTERFACE_MAPPING
from opengever.dossier.vocabularies import IRestrictKeywords
from plone import api
from plone.autoform.form import AutoExtensibleForm
from plone.autoform.widgets import ParameterizedWidget
from plone.dexterity.i18n import MessageFactory as pd_mf
from plone.dexterity.interfaces import IDexterityContainer
from plone.supermodel import model
from plone.z3cform.layout import FormWrapper
from z3c.form import button
from z3c.form.button import buttonAndHandler
from z3c.form.form import Form
from z3c.form.interfaces import IDataConverter
from zExceptions import Unauthorized
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
import json


@provider(IContextSourceBinder)
def get_dossier_templates(context):
    """Returns the selected templates when the addable templates are restricted
    by the addable_dossier_templates field, otherwise it returns all templates.
    """

    if IRestrictAddableDossierTemplates(context).addable_dossier_templates:
        templates = [rel.to_object for rel in
                     IRestrictAddableDossierTemplates(context).addable_dossier_templates]

    else:
        brains = api.portal.get_tool('portal_catalog')({
            'portal_type': 'opengever.dossier.dossiertemplate',
            'is_subdossier': False
        })
        templates = [brain.getObject() for brain in brains]

    terms = []
    for template in templates:
        terms.append(SimpleVocabulary.createTerm(
            template,
            template.UID(),
            template.title))

    return SimpleVocabulary(terms)


@implementer(IVocabularyFactory)
class DossierTemplatesVocabulary(object):

    def __call__(self, context):
        if not IRestrictAddableDossierTemplates.providedBy(context):
            return SimpleVocabulary([])
        return get_dossier_templates(context)


def get_wizard_storage_key(context):
    """Return the key used to store template-data in the wizard-storage.
    """
    container_oguid = Oguid.for_object(context)
    return 'add_dossier_from_template:{}'.format(container_oguid)


def set_wizard_storage(context, data):
    storage = getUtility(IWizardDataStorage)
    storage.update(get_wizard_storage_key(context), data)


def get_wizard_storage(context):
    storage = getUtility(IWizardDataStorage)
    return storage.get_data(get_wizard_storage_key(context))


def save_template_obj(context, template):
    set_wizard_storage(context,
                       {'template_path': '/'.join(template.getPhysicalPath())})


def get_saved_template_obj(context):
    template_path = get_wizard_storage(context).get('template_path')
    if not template_path:
        return None

    return api.portal.get().restrictedTraverse(template_path, default=None)


class ICreateDossierFromTemplate(model.Schema):
    """Schema for first wizard step to select the dossiertemplate
    """
    template = TableChoice(
        title=_(u"label_template", default=u"Template"),
        source=get_dossier_templates,
        required=True,
        show_filter=True,
        columns=(
            {'column': 'title',
             'column_title': _(u'label_title', default=u'Title'),
             'sort_index': 'sortable_title'},
            {'column': 'Creator',
             'column_title': _(u'label_creator', default=u'Creator'),
             'sort_index': 'document_author'},
            {'column': 'modified',
             'column_title': _(u'label_modified', default=u'Modified'),
             'transform': helper.readable_date}
        )
    )


class CreateDossierMixin(object):
    """Mixin for all wizard steps to set and name the steps.
    """
    label = _(u'create_dossier_with_template',
              default=u'Create dossier from template')

    steps = [
        ('select-template', _(u'Select dossiertemplate')),
        ('add-dossier-from-template', _(u'Add dossier'))]

    def is_available(self):
        if not self.context.restrictedTraverse(
                'dossier_with_template/is_available')():

            raise(Unauthorized)


class SelectDossierTemplateWizardStep(
        CreateDossierMixin, AutoExtensibleForm, BaseWizardStepForm, Form):
    """First wizard step - select dossiertemplate
    """
    step_name = 'select-template'

    def update(self):
        self.is_available()
        super(SelectDossierTemplateWizardStep, self).update()

    @property
    def schema(self):
        return ICreateDossierFromTemplate

    @button.buttonAndHandler(_('button_continue', default=u'Continue'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        save_template_obj(self.context, data.get('template'))

        return self.request.RESPONSE.redirect(
            "{}/add-dossier-from-template".format(self.context.absolute_url()))

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'), name='cancel')
    def cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())


class CreateDossierContentFromTemplateMixin(object):

    def create_dossier_content_from_template(self, container, template):
        with DeactivatedCatalogIndexing():
            # While generating content, each newly created object
            # will be indexed up to 4 times in the creation process.
            #
            # This is not necessary and takes a long time.
            #
            # Creating all the subdossier without reindexing the catalog
            # will improve the performance massively and we can manually
            # reindex the created objects once at the end of the creation
            # process.
            self.recursive_content_creation(template, container)

        self.recursive_reindex(container)

    def recursive_reindex(self, obj):
        for child_obj in obj.listFolderContents():
            child_obj.reindexObject()

            if IDexterityContainer.providedBy(child_obj):
                self.recursive_reindex(child_obj)

    def recursive_content_creation(self, template_obj, target_container):
        responsible = IDossier(target_container).responsible

        for related_document_template in IDossierTemplate(
                template_obj).related_documents:
            template = related_document_template.to_object
            CreateDocumentFromTemplateCommand(
                target_container, template, template.title).execute()

        for child_obj in template_obj.listFolderContents():
            if IDossierTemplateSchema.providedBy(child_obj):
                dossier = CreateDossierFromTemplateCommand(
                    target_container, child_obj).execute()

                IDossier(dossier).responsible = responsible

                self.recursive_content_creation(child_obj, dossier)
            else:
                CreateDocumentFromTemplateCommand(
                    target_container, child_obj, child_obj.title).execute()


class AddDossierFromTemplateWizardStep(WizzardWrappedAddForm):
    """Second wizard step - add the dossier from previeously selected template.
    """

    typename = 'opengever.dossier.businesscasedossier'

    def _create_form_class(self, parent_form_class, steptitle):
        class WrappedForm(CreateDossierMixin, CreateDossierContentFromTemplateMixin,
                          BaseWizardStepForm, parent_form_class):
            step_name = 'add-dossier-from-template'

            def updateFields(self):
                super(WrappedForm, self).updateFields()
                template_obj = get_saved_template_obj(self.context)

                if template_obj and template_obj.restrict_keywords:
                    # The vocabulary should only contain the terms from the
                    # template. This is indicated to the source with the
                    # IRestrictKeywords interface and the allowed keywords
                    # are stored on the request. We also need to set the widget
                    # in the synchronous mode, as otherwise keyword searches
                    # will anonymously reinitialise a new source with no way of
                    # accessing the IWizardDataStorage and hence the template.
                    alsoProvides(self.request, IRestrictKeywords)
                    self.request.allowed_keywords = IDossierTemplate(template_obj).keywords

                    self.groups[0].fields['IDossier.keywords'].widgetFactory["input"] = ParameterizedWidget(
                        KeywordWidget,
                        async=False
                    )

            def update(self):
                """Update the widget-values of the dossier add-form
                with the values of the selected dossiertemplate values.
                """
                self.is_available()
                super(WrappedForm, self).update()

                if not getSecurityManager().getUser().getId():
                    # this happens during ++widget++ traversal
                    return

                template_obj = get_saved_template_obj(self.context)

                if not template_obj:
                    # This happens if the user access the step directly and
                    # the wizard storage was expired or never existent.
                    return self.request.RESPONSE.redirect(
                        '{}/dossier_with_template'.format(self.context.absolute_url()))

                template_values = template_obj.get_schema_values()
                title_help = IDossierTemplateSchema(template_obj).title_help

                for group in self.groups:
                    for fieldname, widget in group.widgets.items():
                        # We skip fields that do not exist on the dossier template
                        mapped_field_name = self.map_to_template_fieldname(fieldname)
                        if mapped_field_name not in template_values:
                            continue

                        value = template_values.get(mapped_field_name)

                        # If the current field is the title field and the
                        # title_help is set, we remove the input-value and
                        # add a field description with the title_help text
                        # instead.
                        if widget.field == IOpenGeverBase['title'] and title_help:
                            widget.dynamic_description = title_help
                            value = ''

                        # Set the template value to the dossier add-form widget.
                        widget.value = IDataConverter(widget).toWidgetValue(value)

                        if fieldname == 'IDossier.keywords':
                            self._modify_keyword_widget_according_to_template(widget)

            def _modify_keyword_widget_according_to_template(self, widget):
                template_obj = get_saved_template_obj(self.context)

                if template_obj.restrict_keywords:
                    # since the widget gets somehow reinitialized it's not
                    # possible to manipulate the add_permission directly.
                    # Changing other values like something on a field may
                    # lead to unexpected behavior.
                    # This is the insecure option - but it fits for this
                    # usecase
                    select2_config = json.loads(widget.config_json)
                    select2_config['tags'] = False
                    widget.config_json = json.dumps(select2_config)

                if not template_obj.predefined_keywords:
                    widget.value = ()

            def map_to_template_fieldname(self, fieldname):
                """The dossiertemplate has some fields matching IDossier fields,
                but with a different interface name, i.e. IDossierTemplate
                instead of IDossier. So we have to map these IDossier to
                IDossierTemplate to get the corresponding fieldname on the
                dossiertemplate

                Example:

                IDossier.keywords => IDossierTemplate.keywords
                """
                interface_name, name = fieldname.split('.')
                return '.'.join([
                    BEHAVIOR_INTERFACE_MAPPING.get(interface_name, interface_name),
                    name])

            @buttonAndHandler(pd_mf(u'Save'), name='save')
            def handleAdd(self, action):
                data, errors = self.extractData()
                if errors:
                    self.status = self.formErrorsMessage
                    return
                container = self.createAndAdd(data)
                if container is not None:
                    container = self.context.get(container.getId())
                    template_container = get_saved_template_obj(self.context)

                    self.create_dossier_content_from_template(container, template_container)

                    self._finishedAdd = True
                    api.portal.show_message(
                        pd_mf(u"Item created"), request=self.request, type="info")

            @buttonAndHandler(pd_mf(u'Cancel'), name='cancel')
            def handleCancel(self, action):
                return self.request.RESPONSE.redirect(self.context.absolute_url())

        return WrappedForm


class SelectDossierTemplateView(FormWrapper):
    """The wizard itself to add a new dossier from a template.
    """
    form = SelectDossierTemplateWizardStep

    def is_available(self):
        """Checks if it is allowed to add a 'dossier from template'
        at the current context.
        """
        return is_create_dossier_from_template_available(self.context)

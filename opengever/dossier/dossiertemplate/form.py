from AccessControl import getSecurityManager
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
from opengever.dossier.dossiertemplate import is_dossier_template_feature_enabled
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateSchema
from opengever.dossier.dossiertemplate.behaviors import IRestrictAddableDossierTemplates
from opengever.dossier.dossiertemplate.dossiertemplate import BEHAVIOR_INTERFACE_MAPPING
from opengever.dossier.dossiertemplate.dossiertemplate import TEMPLATABLE_FIELDS
from plone import api
from plone.autoform.form import AutoExtensibleForm
from plone.dexterity.i18n import MessageFactory as pd_mf
from plone.dexterity.i18n import MessageFactory as PDMF
from plone.dexterity.interfaces import IDexterityContainer
from plone.supermodel import model
from plone.z3cform.layout import FormWrapper
from z3c.form import button
from z3c.form.button import buttonAndHandler
from z3c.form.form import Form
from z3c.form.interfaces import IDataConverter
from zExceptions import Unauthorized
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
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

    intids = getUtility(IIntIds)
    terms = []
    for template in templates:
        terms.append(SimpleVocabulary.createTerm(
            template,
            str(intids.getId(template)),
            template.title))

    return SimpleVocabulary(terms)


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


class AddDossierFromTemplateWizardStep(WizzardWrappedAddForm):
    """Second wizard step - add the dossier from previeously selected template.
    """

    typename = 'opengever.dossier.businesscasedossier'

    def _create_form_class(self, parent_form_class, steptitle):
        class WrappedForm(CreateDossierMixin, BaseWizardStepForm, parent_form_class):
            step_name = 'add-dossier-from-template'

            def update(self):
                """Update the widget-values of the dossier add-form
                with the values of the selected dossiertemplate values.
                """
                super(WrappedForm, self).update()

                if not getSecurityManager().getUser().getId():
                    # this happens during ++widget++ traversal
                    return

                self.is_available()

                template_obj = get_saved_template_obj(self.context)

                if not template_obj:
                    # This happens if the user access the step directly and
                    # the wizard storage was expired or never existent.
                    return self.request.RESPONSE.redirect(
                        '{}/dossier_with_template'.format(self.context.absolute_url()))

                template_values = template_obj.get_schema_values()
                title_help = IDossierTemplateSchema(template_obj).title_help

                for group in self.groups:
                    for widgetname in group.widgets:

                        # Skip not whitelisted template fields.
                        # We don't want to update fields which are not
                        # whitelisted in the template.
                        template_widget_name = self.get_template_widget_name(widgetname)
                        if template_widget_name not in TEMPLATABLE_FIELDS:
                            continue

                        value = template_values.get(template_widget_name)
                        widget = group.widgets.get(widgetname)

                        # If the current field is the title field and the
                        # title_help is set, we remove the input-value and
                        # add a field description with the title_help text
                        # instead.
                        if widget.field == IOpenGeverBase['title'] and title_help:
                            widget.dynamic_description = title_help
                            value = ''

                        # Set the template value to the dossier add-form widget.
                        widget.value = IDataConverter(widget).toWidgetValue(value)

                        if widgetname == 'IDossier.keywords':
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

                    # The vocabular should only contain the terms from
                    # the template.
                    terms = filter(
                        lambda term: term.token in widget.value,
                        widget.terms.terms._terms)
                    widget.terms.terms = SimpleVocabulary(terms)

                if not template_obj.predefined_keywords:
                    widget.value = ()

            def get_template_widget_name(self, widgetname):
                """The dossiertemplates uses the same fields as the
                dossier (IDossier) but it includes it with another interface.
                We have to map this two interface names to get the correct
                value or widget.

                This function maps an original interface to the DossierTemplate
                interfaces:

                Example:

                IDossier.keywords => IDossierTemplate.keywords
                """
                interface_name, name = widgetname.split('.')
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
                        self.recursive_content_creation(template_container, container)

                    self.recursive_reindex(container)

                    self._finishedAdd = True
                    api.portal.show_message(
                        PDMF(u"Item created"), request=self.request, type="info")

            @buttonAndHandler(pd_mf(u'Cancel'), name='cancel')
            def handleCancel(self, action):
                return self.request.RESPONSE.redirect(self.context.absolute_url())

            def recursive_reindex(self, obj):
                for child_obj in obj.listFolderContents():
                    child_obj.reindexObject()

                    if IDexterityContainer.providedBy(child_obj):
                        self.recursive_reindex(child_obj)

            def recursive_content_creation(self, template_obj, target_container):
                responsible = IDossier(target_container).responsible

                for child_obj in template_obj.listFolderContents():
                    if IDossierTemplateSchema.providedBy(child_obj):
                        dossier = CreateDossierFromTemplateCommand(
                            target_container, child_obj).execute()

                        IDossier(dossier).responsible = responsible

                        self.recursive_content_creation(child_obj, dossier)
                    else:
                        CreateDocumentFromTemplateCommand(
                            target_container, child_obj, child_obj.title).execute()

        return WrappedForm


class SelectDossierTemplateView(FormWrapper):
    """The wizard itself to add a new dossier from a template.
    """
    form = SelectDossierTemplateWizardStep

    def is_available(self):
        """Checks if it is allowed to add a 'dossier from template'
        at the current context.
        """
        return is_dossier_template_feature_enabled() and \
            self.context.is_leaf_node() and \
            api.user.has_permission('opengever.dossier: Add businesscasedossier', obj=self.context) and \
            (self.context.allow_add_businesscase_dossier or self.context.addable_dossier_templates)

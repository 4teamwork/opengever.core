from copy import deepcopy
from opengever.base.schema import TableChoice
from opengever.oneoffixx import _
from opengever.oneoffixx.api_client import OneoffixxAPIClient
from opengever.oneoffixx.command import CreateDocumentFromOneOffixxTemplateCommand
from opengever.oneoffixx.utils import whitelisted_template_types
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from plone.supermodel import model
from plone.z3cform.layout import FormWrapper
from z3c.form import button
from z3c.form.field import Fields
from z3c.form.form import Form
from zope import schema
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary


def get_oneoffixx_favorites():
    """Return the user chosen favorites as a template group, if any."""
    api_client = OneoffixxAPIClient()
    favorites = api_client.get_oneoffixx_favorites()
    if favorites.get('templates'):
        return favorites
    return None


def get_oneoffixx_template_groups():
    """Return the template groups.

    Potentially amended with user chosen favorites.
    """
    api_client = OneoffixxAPIClient()
    # We need to work on a copy to not pollute the cached one
    template_groups = deepcopy(api_client.get_oneoffixx_template_groups())
    favorites = get_oneoffixx_favorites()
    if favorites:
        template_groups.insert(0, favorites)
    return template_groups


def get_oneoffixx_templates():
    """Return all oneoffixx templates.

    We do not want duplicates from favorites here.
    """
    api_client = OneoffixxAPIClient()
    return (
        OneOffixxTemplate(template, template_group.get('localizedName', ''))
        for template_group in api_client.get_oneoffixx_template_groups()
        for template in template_group.get("templates")
        if template.get('metaTemplateId') in whitelisted_template_types
    )


def default_template_group():
    """Return all templates, or the user favorites, if defined by user."""
    favorites = get_oneoffixx_favorites()
    if favorites:
        return favorites.get('id')
    return None


@provider(IContextSourceBinder)
def list_templates(context):
    """Return a list available templates."""
    templates = get_oneoffixx_templates()
    template_group = context.REQUEST.form.get('form.widgets.template_group')
    terms = []

    for template in templates:
        terms.append(SimpleVocabulary.createTerm(
            template, template.template_id, template.title))

    # We filter templates when template_group has been selected
    if template_group is not None:
        favorites = get_oneoffixx_favorites()
        # Favorites are a special case
        if favorites and template_group[0] == favorites.get('id'):
            terms = [
                SimpleVocabulary.createTerm(
                    OneOffixxTemplate(
                        template, favorites.get('localizedName', '')),
                    template.get('id'),
                    template.get('localizedName'),
                )
                for template in favorites.get('templates')
            ]
        elif template_group[0] != '--NOVALUE--':
            terms = [term for term in terms if term.value.group == template_group[0]]

    return MutableObjectVocabulary(terms)


@provider(IContextSourceBinder)
def list_template_groups(context):
    """Return the list of available template groups."""
    template_groups = get_oneoffixx_template_groups()
    terms = []
    for group in template_groups:
        terms.append(SimpleVocabulary.createTerm(group.get("id"),
                                                 group.get("id"),
                                                 group.get("localizedName")))
    return MutableObjectVocabulary(terms)


class OneOffixxTemplate(object):

    def __init__(self, template, groupname):
        self.title = template.get("localizedName")
        self.template_id = template.get("id")
        self.group = template.get('templateGroupId')
        self.groupname = groupname
        template_type = template['metaTemplateId']
        template_type_info = whitelisted_template_types[template_type]
        self.content_type = template_type_info['content-type']
        filename = template.get("localizedName")
        normalizer = getUtility(IFileNameNormalizer, name='gever_filename_normalizer')
        self.filename = normalizer.normalize(filename, extension=template_type_info['extension'])
        self.languages = template.get("languages")

    def __eq__(self, other):
        if type(other) == type(self):
            return self.template_id == other.template_id
        return False


class MutableObjectVocabulary(SimpleVocabulary):

    def __contains__(self, value):
        try:
            return any([value == val for val in self.by_value])
        except TypeError:
            return False


class ICreateDocumentFromOneOffixxTemplate(model.Schema):

    # XXX - this always renders the --NOVALUE-- as the actually chosen
    # default is actually loaded over AJAX - confusing and bad UX
    template_group = schema.Choice(
        title=_(u'label_template_group', default=u'Template group'),
        source=list_template_groups,
        required=False,
        defaultFactory=default_template_group,
    )

    template = TableChoice(
        title=_(u"label_template", default=u"Template"),
        source=list_templates,
        required=True,
        show_filter=False,
        vocabulary_depends_on=['form.widgets.template_group'],
        columns=(
            {'column': 'title',
             'column_title': _(u'label_title', default=u'Title'),
             'sort_index': 'sortable_title'},
            )
    )

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        required=True)


class SelectOneOffixxTemplateDocumentWizardStep(Form):

    label = _(u'create_document_with_template', default=u'Create document from template')
    ignoreContext = True
    fields = Fields(ICreateDocumentFromOneOffixxTemplate)

    def updateWidgets(self, prefix=None):
        super(SelectOneOffixxTemplateDocumentWizardStep, self).updateWidgets(prefix=prefix)
        self.widgets['template_group'].noValueMessage = translate(
            _(u'label_all_template_groups', default=u'All templates'), context=self.request)

    def finish_document_creation(self, data):
        new_doc = self.create_document(data)
        self.activate_external_editing(new_doc)
        return self.request.RESPONSE.redirect(new_doc.absolute_url())

    def activate_external_editing(self, new_doc):
        """Add the oneoffixx external_editor URL to redirector queue."""
        new_doc.setup_external_edit_redirect(self.request, action="oneoffixx")

    def create_document(self, data):
        """Create a new document based on a template."""
        command = CreateDocumentFromOneOffixxTemplateCommand(self.context, data['title'], data['template'])
        return command.execute()

    @button.buttonAndHandler(_('button_save', default=u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()

        if not errors:
            return self.finish_document_creation(data)

        self.status = self.formErrorsMessage
        return None

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'), name='cancel')
    def cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())


class SelectOneOffixxTemplateDocumentView(FormWrapper):

    form = SelectOneOffixxTemplateDocumentWizardStep

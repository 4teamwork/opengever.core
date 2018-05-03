from opengever.base.schema import TableChoice
from opengever.dossier import _
from opengever.oneoffixx.command import CreateDocumentFromOneOffixxTemplateCommand
from plone.supermodel import model
from plone.z3cform.layout import FormWrapper
from z3c.form import button
from z3c.form.form import Form
from z3c.form.field import Fields
from zope import schema
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary


def get_template_groups():
    templates = [
                 {'templates': [
                                {u'languages': [2055],
                                 u'localizedName': u'Brief schwarz/weiss',
                                 u'templateGroupId': u'14ff1ebc-ba0c-4732-93e2-829fe6cc6bc6',
                                 u'id': u'52945b6c-b65a-436d-8045-619e4e41af51'},
                                {u'languages': [2055],
                                 u'localizedName': u'Brief farbig',
                                 u'templateGroupId': u'14ff1ebc-ba0c-4732-93e2-829fe6cc6bc6',
                                 u'id': u'06149cd5-efe1-47e5-a822-993fa1b65ef0'},
                                {u'languages': [2055],
                                 u'localizedName': u'Kurzbrief',
                                 u'templateGroupId': u'14ff1ebc-ba0c-4732-93e2-829fe6cc6bc6',
                                 u'id': u'2574d08d-95ea-4639-beab-3103fe4c3bc7'},
                                ],
                  u'id':u'14ff1ebc-ba0c-4732-93e2-829fe6cc6bc6',
                  u'localizedName': u'Korrespondenz'
                  },
                 {'templates': [
                                {u'languages': [2055],
                                 u'localizedName': u'Entwurf Bericht/Botschaft',
                                 u'templateGroupId': u'3a66d83c-077c-4917-aef6-6d4765af1126',
                                 u'id': u'8b82b8c1-6780-4c5c-8229-00da90f96b15'},
                                {u'languages': [2055],
                                 u'localizedName': u'Antwort Vorstoss',
                                 u'templateGroupId': u'3a66d83c-077c-4917-aef6-6d4765af1126',
                                 u'id': u'810b1174-f12e-4e43-959e-d5fda1e7f0e2'},
                                ],
                  u'id': u'3a66d83c-077c-4917-aef6-6d4765af1126',
                  u'localizedName': u'Kantonsrat'
                  }
                ]
    return templates


def get_oneoffixx_templates():
    templates = (OneOffixxTemplate(template)
                 for template_group in get_template_groups()
                 for template in template_group.get("templates"))
    return templates


@provider(IContextSourceBinder)
def list_templates(context):
    """Return a list available templates
    """

    templates = get_oneoffixx_templates()

    template_group = context.REQUEST.form.get('form.widgets.template_group')
    terms = []
    for template in templates:
        terms.append(SimpleVocabulary.createTerm(
                     template,
                     str(template.template_id),
                     template.title))

    # filter templates when template_group has been selected
    if template_group is not None and template_group[0] != '--NOVALUE--':
        terms = [term for term in terms if term.value.group == template_group[0]]
    return MutableObjectVocabulary(terms)


@provider(IContextSourceBinder)
def list_template_groups(context):
    """Return the list of available template groups
    """
    template_groups = get_template_groups()
    terms = []
    for group in template_groups:
        terms.append(SimpleVocabulary.createTerm(group.get("id"),
                                                 group.get("id"),
                                                 group.get("localizedName")))
    return MutableObjectVocabulary(terms)


class OneOffixxTemplate(object):

    def __init__(self, template):
        self.title = template.get("localizedName")
        self.template_id = template.get("id")
        self.group = template.get('templateGroupId')
        self.filename = unicode(template.get("localizedName"))
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

    template_group = schema.Choice(
        title=_(u'label_template_group', default=u'Template group'),
        source=list_template_groups,
        required=False,
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

    label = _(u'create_document_with_template',
              default=u'Create document from template')
    ignoreContext = True
    fields = Fields(ICreateDocumentFromOneOffixxTemplate)

    def finish_document_creation(self, data):
        new_doc = self.create_document(data)
        self.activate_external_editing(new_doc)
        return self.request.RESPONSE.redirect(
                new_doc.absolute_url())

    def activate_external_editing(self, new_doc):
        """Add the oneoffixx external_editor URL to redirector queue.
        """

        new_doc.setup_external_edit_redirect(self.request, action="oneoffixx")

    def create_document(self, data):
        """Create a new document based on a template."""

        command = CreateDocumentFromOneOffixxTemplateCommand(
            self.context, data['title'], data['template'])
        return command.execute()

    @button.buttonAndHandler(_('button_save', default=u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage
            return

        return self.finish_document_creation(data)

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'), name='cancel')
    def cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())


class SelectOneOffixxTemplateDocumentView(FormWrapper):

    form = SelectOneOffixxTemplateDocumentWizardStep

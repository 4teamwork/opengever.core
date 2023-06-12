from ftw.keywordwidget.field import ChoicePlus
from ftw.keywordwidget.widget import KeywordFieldWidget
from ftw.tabbedview.interfaces import ITabbedviewUploadable
from opengever.base import _ as base_mf
from opengever.base.source import SolrObjPathSourceBinder
from opengever.base.vocabulary import wrap_vocabulary
from opengever.dossier import _
from opengever.dossier.behaviors import dossiernamefromtitle
from opengever.dossier.behaviors.dossier import CHECKLIST_SCHEMA
from opengever.dossier.vocabularies import KeywordAddableRestrictableSourceBinder
from plone.app.content.interfaces import INameFromTitle
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.schema import JSONField
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import Interface


class IDossierTemplateSchema(model.Schema):
    """Schema interface for dossier template types.

    Use this type of dossier to create a reusable template structures.
    """

    model.fieldset(
        u'common',
        label=base_mf(u'fieldset_common', default=u'Common'),
        fields=[
            u'title_help',
            u'predefined_keywords',
            u'restrict_keywords',
        ],
    )

    title_help = schema.TextLine(
        title=_(u'label_title_help', default=u'Title help'),
        description=_(u'help_title_help',
                      default=u'Recommendation for the title. Will be '
                              u'displayed as a help text if you create '
                              u'a dossier from template'),
        required=False,
        missing_value=u'',
        default=u'',
    )

    form.order_after(predefined_keywords='IDossierTemplate.keywords')
    predefined_keywords = schema.Bool(
        title=_(u'label_predefined_keywords', default=u'Predefined Keywords'),
        description=_(u'description_predefined_keywords',
                      default=u'The defined keywords will be preselected for '
                              u'new dossies from template.'),
        required=False,
        missing_value=True,
        default=True,
    )

    form.order_after(restrict_keywords='predefined_keywords')
    restrict_keywords = schema.Bool(
        title=_(u'label_restrict_keywords', default=u'Restrict Keywords'),
        description=_(u'description_restrict_keywords',
                      default=u'The user can choose only from the defined keywords '
                              u'in a new dossier from template. It also prevents '
                              u'the user for creating new keywords'),
        required=False,
        missing_value=False,
        default=False,
    )


class IDossierTemplateMarker(Interface, ITabbedviewUploadable):
    """Marker Interface for dossiertemplates.
    """


class IDossierTemplate(model.Schema):
    """Behavior Interface for dossiertemplates.
    """

    model.fieldset(
        u'common',
        label=base_mf(u'fieldset_common', default=u'Common'),
        fields=[
            u'keywords',
            u'dossier_type',
            u'checklist',
            u'related_documents',
        ],
    )

    form.widget('keywords', KeywordFieldWidget, new_terms_as_unicode=True, async=True)
    keywords = schema.Tuple(
        title=_(u'label_keywords', default=u'Keywords'),
        description=_(u'help_keywords', default=u''),
        value_type=ChoicePlus(
            source=KeywordAddableRestrictableSourceBinder()
        ),
        required=False,
        missing_value=(),
        default=(),
    )

    dossier_type = schema.Choice(
        title=_(u'label_dossier_type', default='Dossier type'),
        source=wrap_vocabulary(
            'opengever.dossier.dossier_types',
            hidden_terms_from_registry='opengever.dossier.interfaces.IDossierType.hidden_dossier_types'),
        required=False,
    )

    related_documents = RelationList(
        title=_(u'label_related_documents',
                default=u'Related documents'),
        default=list(),
        missing_value=list(),
        value_type=RelationChoice(
            title=u'Related document templates',
            source=SolrObjPathSourceBinder(
                object_provides=("opengever.document.interfaces.ITemplateDocumentMarker", ),
                navigation_tree_query={
                    'object_provides':
                    ['opengever.dossier.templatefolder.interfaces.ITemplateFolder',
                     'opengever.document.document.IDocumentSchema']
                }),
        ),
        required=False,
    )

    model.fieldset(
        u'filing',
        label=_(u'fieldset_filing', default=u'Filing'),
        fields=[
            u'filing_prefix',
        ],
    )

    filing_prefix = schema.Choice(
        title=_(u'filing_prefix', default="filing prefix"),
        source=wrap_vocabulary(
            'opengever.dossier.type_prefixes',
            visible_terms_from_registry="opengever.dossier"
            '.interfaces.IDossierContainerTypes.type_prefixes'),
        required=False,
    )

    checklist = JSONField(
        title=_(u'label_checklist', default=u'Checklist'),
        required=False,
        schema=CHECKLIST_SCHEMA,
    )


alsoProvides(IDossierTemplate, IFormFieldProvider)


class IDossierTemplateNameFromTitle(INameFromTitle):
    """Behavior interface.
    """


class DossierTemplateNameFromTitle(dossiernamefromtitle.DossierNameFromTitle):
    """Choose IDs for a dossiertemplate in the following format:
    'dossiertemplate-{sequence number}'
    """

    implements(IDossierTemplateNameFromTitle)

    format = u'dossiertemplate-%i'


class IRestrictAddableDossierTemplates(model.Schema):

    model.fieldset(
        u'common',
        label=base_mf(u'fieldset_common', default=u'Common'),
        fields=[
            u'addable_dossier_templates',
        ],
    )

    addable_dossier_templates = RelationList(
        title=_(u'label_addable_dossier_templates',
                default=u'Addable dossier templates'),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u'Addable dossiertemplate',
            source=SolrObjPathSourceBinder(
                portal_type=("opengever.dossier.dossiertemplate"),
                is_subdossier=False,
                navigation_tree_query={
                    'object_provides':
                    ['opengever.dossier.templatefolder.interfaces.ITemplateFolder',
                     'opengever.dossier.dossiertemplate.behaviors.IDossierTemplateSchema']
                }),
        ),
        required=False,
    )


alsoProvides(IRestrictAddableDossierTemplates, IFormFieldProvider)

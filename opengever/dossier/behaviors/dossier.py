from collective.elephantvocabulary import wrap_vocabulary
from datetime import date
from ftw.datepicker.widget import DatePickerFieldWidget
from ftw.keywordwidget.field import ChoicePlus
from ftw.keywordwidget.widget import KeywordFieldWidget
from ftw.tabbedview.interfaces import ITabbedviewUploadable
from opengever.base.source import RepositoryPathSourceBinder
from opengever.dossier import _
from opengever.dossier.vocabularies import KeywordAddableRestrictableSourceBinder
from opengever.dossier.widget import referenceNumberWidgetFactory
from opengever.ogds.base.sources import AssignedUsersSourceBinder
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.i18n import MessageFactory as pd_mf  # noqa
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant
import logging

LOG = logging.getLogger('opengever.dossier')


class IDossierMarker(Interface, ITabbedviewUploadable):
    """Marker Interface for dossiers.
    """


def start_date_default():
    return date.today()


class IDossier(model.Schema):
    """Behaviour interface for dossier types providing
    common properties/fields.
    """

    model.fieldset(
        u'common',
        label=_(u'fieldset_common', u'Common'),
        fields=[
            u'keywords',
            u'start',
            u'end',
            u'comments',
            u'external_reference',
            u'responsible',
            u'relatedDossier',
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

    # workaround because ftw.datepicker wasn't working on the edit form
    form.widget(start=DatePickerFieldWidget)
    start = schema.Date(
        title=_(u'label_start', default=u'Opening Date'),
        required=False,
        defaultFactory=start_date_default,
    )

    # workaround because ftw.datepicker wasn't working on the edit form
    form.widget(end=DatePickerFieldWidget)
    end = schema.Date(
        title=_(u'label_end', default=u'Closing Date'),
        required=False,
    )

    comments = schema.Text(
        title=_(u'label_comments', default=u'Comments'),
        required=False,
    )

    form.widget('responsible', KeywordFieldWidget, async=True)
    responsible = schema.Choice(
        title=_(u"label_responsible", default="Responsible"),
        source=AssignedUsersSourceBinder(),
        required=True,
    )

    external_reference = schema.TextLine(
        title=_(u'label_external_reference', default=u'External Reference'),
        required=False,
    )

    model.fieldset(
        u'filing',
        label=_(u'fieldset_filing', default=u'Filing'),
        fields=[
            u'filing_prefix',
            u'container_type',
            u'number_of_containers',
            u'container_location',
            u'reference_number',
            u'former_reference_number',
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

    # needed for temporarily storing current reference number when
    # moving this dossier
    form.omitted('temporary_former_reference_number')
    temporary_former_reference_number = schema.TextLine(
        title=_(u'temporary_former_reference_number',
                default="Temporary former reference number"),
        required=False,
    )

    container_type = schema.Choice(
        title=_(u'label_container_type', default=u'Container Type'),
        description=_(u'help_container_type', default=u''),
        source=wrap_vocabulary(
            'opengever.dossier.container_types',
            visible_terms_from_registry="opengever.dossier"
            '.interfaces.IDossierContainerTypes.container_types'),
        required=False,
    )

    number_of_containers = schema.Int(
        title=_(u'label_number_of_containers',
                default=u'Number of Containers'),
        description=_(u'help_number_of_containers', default=u''),
        required=False,
    )

    container_location = schema.TextLine(
        title=_(u'label_container_location', default=u'Container Location'),
        description=_(u'help_container_location', default=u''),
        required=False,
    )

    relatedDossier = RelationList(
        title=_(u'label_related_dossier', default=u'Related Dossier'),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u"Related",
            source=RepositoryPathSourceBinder(
                object_provides='opengever.dossier.behaviors.dossier.'
                'IDossierMarker',
                navigation_tree_query={
                    'object_provides': [
                        'opengever.repository.repositoryroot.IRepositoryRoot',
                        'opengever.repository.repositoryfolder.'
                        'IRepositoryFolderSchema',
                        'opengever.dossier.behaviors.dossier.IDossierMarker',
                    ]
                }),
        ),
        required=False,
    )

    form.mode(former_reference_number='display')
    former_reference_number = schema.TextLine(
        title=_(u'label_former_reference_number',
                default=u'Reference Number'),
        required=False,
    )

    form.widget(reference_number=referenceNumberWidgetFactory)
    form.mode(reference_number='display')
    reference_number = schema.TextLine(
        title=_(u'label_reference_number', default=u'Reference Number'),
        required=False,
        readonly=True,
    )

    @invariant
    def validate_start_end(data):
        # Do not get the data from the context when it is not in the current
        # fields / z3cform group
        data = data._Data_data___

        if 'start' not in data or 'end' not in data:
            return

        if data['start'] is not None and data['end'] is not None:
            if data['start'] > data['end']:
                raise StartBeforeEnd(
                    _(u"The start date must be before the end date."))


alsoProvides(IDossier, IFormFieldProvider)


class StartBeforeEnd(Invalid):
    __doc__ = _(u"The start or end date is invalid")

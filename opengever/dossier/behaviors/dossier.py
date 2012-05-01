from AccessControl import getSecurityManager
from Acquisition import aq_inner, aq_parent
from collective import dexteritytextindexer
from collective.elephantvocabulary import wrap_vocabulary
from datetime import datetime
from five import grok
from ftw.datepicker.widget import DatePickerFieldWidget
from ftw.tabbedview.interfaces import ITabbedviewUploadable
from opengever.base.source import RepositoryPathSourceBinder
from opengever.dossier import _
from opengever.dossier.widget import referenceNumberWidgetFactory
from opengever.mail.interfaces import ISendableDocsContainer
from opengever.ogds.base.autocomplete_widget import AutocompleteFieldWidget
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.i18n import MessageFactory as pd_mf
from plone.dexterity.interfaces import IDexterityFTI
from plone.directives import form, dexterity
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from z3c.relationfield.schema import RelationChoice, RelationList
from zope import schema
from zope.component import getUtility
from zope.interface import Interface, alsoProvides
from zope.interface import invariant, Invalid
import logging


LOG = logging.getLogger('opengever.dossier')


class IDossierMarker(Interface, ISendableDocsContainer, ITabbedviewUploadable):
    """ Marker Interface for dossiers.
    """


class IDossier(form.Schema):
    """ Behaviour interface for dossier types providing
    common properties/fields.
    """

    form.fieldset(
        u'common',
        fields=[
            u'keywords',
            u'start',
            u'end',
            u'comments',
            u'responsible',
            u'relatedDossier',
            ],
        )

    dexteritytextindexer.searchable('keywords')
    keywords = schema.Tuple(
        title=_(u'label_keywords', default=u'Keywords'),
        description=_(u'help_keywords', default=u''),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
        )
    form.widget(keywords=TextLinesFieldWidget)

    #workaround because ftw.datepicker wasn't working on the edit form
    form.widget(start=DatePickerFieldWidget)
    start = schema.Date(
        title=_(u'label_start', default=u'Opening Date'),
        description=_(u'help_start', default=u''),
        required=False,
        )

    #workaround because ftw.datepicker wasn't working on the edit form
    form.widget(end=DatePickerFieldWidget)
    end = schema.Date(
        title=_(u'label_end', default=u'Closing Date'),
        description=_(u'help_end', default=u''),
        required=False,
        )

    comments = schema.Text(
        title=_(u'label_comments', default=u'Comments'),
        description=_(u'help_comments', default=u''),
        required=False,
        )

    form.widget(responsible=AutocompleteFieldWidget)
    responsible = schema.Choice(
        title=_(u"label_responsible", default="Responsible"),
        description=_(
            u"help_responsible", default="Select the responsible manager"),
        vocabulary=u'opengever.ogds.base.AssignedUsersVocabulary',
        required=True,
        )

    form.fieldset(
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
            visible_terms_from_registry="opengever.dossier" + \
                '.interfaces.IDossierContainerTypes.type_prefixes'),
        required=False,
        )

    form.omitted('filing_no')
    filing_no = schema.TextLine(
        title=_(u'filing_no', default="Filing number"),
        description=_(u'help_filing_no', default=u''),
        required=False,
        )

    # needed for temporarily storing current reference number when
    # moving this dossier
    form.omitted('temporary_former_reference_number')
    temporary_former_reference_number = schema.TextLine(
        title=_(u'temporary_former_reference_number',
                default="Temporary former reference number"),
        description=_(u'help_temporary_former_reference_number', default=u''),
        required=False,
        )

    container_type = schema.Choice(
        title=_(u'label_container_type', default=u'Container Type'),
        description=_(u'help_container_type', default=u''),
        source=wrap_vocabulary(
            'opengever.dossier.container_types',
            visible_terms_from_registry="opengever.dossier" + \
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
        value_type=RelationChoice(
            title=u"Related",
            source=RepositoryPathSourceBinder(
                object_provides='opengever.dossier.behaviors.dossier.' + \
                    'IDossierMarker',
                navigation_tree_query={
                    'object_provides': [
                        'opengever.repository.repositoryroot.IRepositoryRoot',
                        'opengever.repository.repositoryfolder.' + \
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
        description=_(u'help_former_reference_number', default=u''),
        required=False,
        )

    form.widget(reference_number=referenceNumberWidgetFactory)
    reference_number = schema.TextLine(
        title=_(u'label_reference_number', default=u'Reference Number'),
        description=_(u'help_reference_number ', default=u''),
        required=False,
        )

    @invariant
    def validateStartEnd(data):
        if data.start is not None and data.end is not None:
            if data.start > data.end:
                raise StartBeforeEnd(
                    _(u"The start date must be before the end date."))

alsoProvides(IDossier, IFormFieldProvider)


# TODO: temporary default value (autocompletewidget)
class AddForm(dexterity.AddForm):
    grok.name('opengever.dossier.businesscasedossier')

    def update(self):
        """Adds a default value for `responsible` to the request so the
        field is prefilled with the current user, or the parent dossier's
        responsible in the case of a subdossier.
        """
        responsible = getSecurityManager().getUser().getId()
        if IDossierMarker.providedBy(self.context):
            # If adding a subdossier, use parent's responsible
            parent_dossier = IDossier(self.context)
            if parent_dossier:
                responsible = parent_dossier.responsible
        if not self.request.get('form.widgets.IDossier.responsible', None):
            self.request.set('form.widgets.IDossier.responsible',
                             [responsible])
        super(AddForm, self).update()

    @property
    def label(self):
        if IDossierMarker.providedBy(self.context):
            return _(u'Add Subdossier')
        else:
            portal_type = self.portal_type
            fti = getUtility(IDexterityFTI, name=portal_type)
            type_name = fti.Title()
            return pd_mf(u"Add ${name}", mapping={'name': type_name})


class EditForm(dexterity.EditForm):
    """Standard Editform, provide just a special label for subdossiers"""
    grok.context(IDossierMarker)

    @property
    def label(self):
        if IDossierMarker.providedBy(aq_parent(aq_inner(self.context))):
            return _(u'Edit Subdossier')
        else:
            type_name = self.fti.Title()
            return pd_mf(u"Edit ${name}", mapping={'name': type_name})


class StartBeforeEnd(Invalid):
    __doc__ = _(u"The start or end date is invalid")


@form.default_value(field=IDossier['start'])
def deadlineDefaultValue(data):
    return datetime.today()

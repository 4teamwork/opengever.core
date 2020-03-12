from datetime import date
from datetime import timedelta
from ftw.datepicker.widget import DatePickerFieldWidget
from ftw.keywordwidget.widget import KeywordWidget
from opengever.advancedsearch import _
from opengever.ogds.base.sources import AllUsersSourceBinder
from opengever.ogds.base.sources import UsersContactsInboxesSourceBinder
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.models.service import ogds_service
from opengever.task.util import getTaskTypeVocabulary
from plone.autoform.widgets import ParameterizedWidget
from plone.supermodel import model
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as PMF
from z3c.form import button
from z3c.form.browser import radio, checkbox
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import INPUT_MODE
from zope import schema
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
import urllib


@provider(IContextSourceBinder)
def get_possible_dossier_states(context):
    wftool = getToolByName(context, 'portal_workflow')
    chain = wftool.getChainForPortalType(
        'opengever.dossier.businesscasedossier')[0]
    states = []
    for state in wftool.get(chain).states:
        states.append(SimpleVocabulary.createTerm(state, state, PMF(state)))
    return SimpleVocabulary(states)


@provider(IContextSourceBinder)
def get_possible_task_states(context):
    wftool = getToolByName(context, 'portal_workflow')
    chain = wftool.getChainForPortalType(
        'opengever.task.task')[0]
    states = []
    for state in wftool.get(chain).states:
        states.append(SimpleVocabulary.createTerm(state, state, PMF(state)))
    return SimpleVocabulary(states)


@provider(IContextSourceBinder)
def get_types(context):
    types = []
    types.append(SimpleVocabulary.createTerm(
        'opengever.dossier.behaviors.dossier.IDossierMarker',
        'opengever.dossier.behaviors.dossier.IDossierMarker',
        _('dossier')
        )
    )
    types.append(SimpleVocabulary.createTerm(
        'opengever.task.task.ITask',
        'opengever.task.task.ITask',
        _('task')
        )
    )
    types.append(SimpleVocabulary.createTerm(
        'opengever.document.behaviors.IBaseDocument',
        'opengever.document.behaviors.IBaseDocument',
        _('document')
        )
    )
    return SimpleVocabulary(types)


FIELD_MAPPING = {'opengever-dossier-behaviors-dossier-IDossierMarker': [
                    'start_1',
                    'start_2',
                    'end_1',
                    'end_2',
                    'reference',
                    'sequence_number',
                    'responsible',
                    'dossier_review_state',
                ],
                'opengever-task-task-ITask': [
                    'issuer',
                    'deadline_1',
                    'deadline_2',
                    'task_type',
                    'task_review_state',
                ],
                'opengever-document-behaviors-IBaseDocument': [
                    'receipt_date_1',
                    'receipt_date_2',
                    'delivery_date_1',
                    'delivery_date_2',
                    'document_date_1',
                    'document_date_2',
                    'document_author',
                    'checked_out',
                    'trashed',
                ],
                }


def strip_parantheses(value):
    bad_chars = ["(", ")"]
    for char in bad_chars:
        value = value.replace(char, ' ')
    return value


class IAdvancedSearch(model.Schema):

    searchableText = schema.TextLine(
        title=_('label_searchable_text', default='Text'),
        description=_('help_searchable_text', default=''),
        required=False,
    )

    object_provides = schema.Choice(
        title=_('label_portal_type', default="Type"),
        description=_('help_portal_type',
                      default='Select the contenttype to be searched for.'),
        source=get_types,
        required=True,
    )

    # Dossier
    start_1 = schema.Date(
        title=_('label_start', default='Start date'),
        description=_('label_from', default='From'),
        required=False,
    )

    start_2 = schema.Date(
        description=_('label_to', default='To'),
        required=False,
    )

    end_1 = schema.Date(
        title=_('label_end', default='End date'),
        description=_('label_from', default='From'),
        required=False,
    )

    end_2 = schema.Date(
        description=_('label_to', default='To'),
        required=False,
    )

    reference = schema.TextLine(
        title=_('label_reference_number', default='Reference number'),
        description=_('help_reference_number', default=''),
        required=False,
    )

    sequence_number = schema.Int(
        title=_('label_sequence_number', default='Sequence number'),
        description=_('help_sequence_number', default=''),
        required=False,
    )

    responsible = schema.Choice(
        title=_('label_reponsible', default='Responsible'),
        source=AllUsersSourceBinder(only_active_orgunits=False),
        required=False,
    )

    dossier_review_state = schema.List(
        title=_('label_review_state', default='State'),
        value_type=schema.Choice(
            source=get_possible_dossier_states,
        ),
        required=False,
    )

    # Document
    receipt_date_1 = schema.Date(
        title=_('label_receipt_date', default='Receipt date'),
        description=_('label_from', default='From'),
        required=False,
    )

    receipt_date_2 = schema.Date(
        description=_('label_to', default='To'),
        required=False,
    )

    delivery_date_1 = schema.Date(
        title=_('label_delivery_date', default='delivery date'),
        description=_('label_from', default='From'),
        required=False,
    )

    delivery_date_2 = schema.Date(
        description=_('label_to', default='To'),
        required=False,
    )

    document_date_1 = schema.Date(
        title=_('label_document_date', default='Document Date'),
        description=_('label_from', default='From'),
        required=False,
    )

    document_date_2 = schema.Date(
        description=_('label_to', default='To'),
        required=False,
    )

    document_author = schema.TextLine(
        title=_('label_document_author', default='Document author'),
        required=False,
    )

    checked_out = schema.Choice(
        title=_('label_checked_out', default='Checked out by'),
        source=AllUsersSourceBinder(only_active_orgunits=False),
        required=False,
    )

    trashed = schema.Bool(
        title=_('label_trashed', default='Also search in the recycle bin'),
        required=False,
    )

    # Task
    issuer = schema.Choice(
        title=_(u"label_issuer", default=u"Issuer"),
        description=_('help_issuer', default=u""),
        source=UsersContactsInboxesSourceBinder(only_active_orgunits=False),
        required=False,
    )

    deadline_1 = schema.Date(
        title=_('label_deadline', default='Deadline'),
        description=_('label_from', default='From'),
        required=False,
    )

    deadline_2 = schema.Date(
        title=u'',
        description=_('label_to', default='To'),
        required=False,
    )

    task_type = schema.Choice(
        title=_('label_tasktype', default=''),
        source=getTaskTypeVocabulary,
        required=False,
    )
    task_review_state = schema.List(
        title=_('label_review_state', default='State'),
        value_type=schema.Choice(
            source=get_possible_task_states,
        ),
        required=False,
    )


class AdvancedSearchForm(Form):

    label = _('advanced_search', default='advanced search')

    schemas = (IAdvancedSearch,)

    ignoreContext = True

    enable_unload_protection = False

    def field_mapping(self):
        return FIELD_MAPPING

    def get_fields(self):
        if getattr(self, '_fields', None) is not None:
            return self._fields

        fields = Fields(*self.schemas)

        fields['responsible'].widgetFactory[INPUT_MODE] = ParameterizedWidget(
            KeywordWidget,
            async=True
        )
        fields['checked_out'].widgetFactory[INPUT_MODE] = ParameterizedWidget(
            KeywordWidget,
            async=True
        )
        fields['issuer'].widgetFactory[INPUT_MODE] = ParameterizedWidget(
            KeywordWidget,
            async=True
        )
        fields['object_provides'].widgetFactory[INPUT_MODE] \
            = radio.RadioFieldWidget
        fields['dossier_review_state'].widgetFactory[INPUT_MODE] \
            = checkbox.CheckBoxFieldWidget
        fields['task_review_state'].widgetFactory[INPUT_MODE] \
            = checkbox.CheckBoxFieldWidget

        date_fields = [
            'start_1',
            'start_2',
            'end_1',
            'end_2',
            'deadline_1',
            'deadline_2',
            'receipt_date_1',
            'receipt_date_2',
            'delivery_date_1',
            'delivery_date_2',
            'document_date_1',
            'document_date_2',
        ]

        for field in date_fields:
            fields.get(
                field).widgetFactory[INPUT_MODE] = DatePickerFieldWidget

        self._fields = fields
        self.move_fields()
        return self._fields

    def set_fields(self, fields):
        self._fields = fields

    def move_fields(self):
        pass

    fields = property(get_fields, set_fields)

    def updateWidgets(self):
        super(AdvancedSearchForm, self).updateWidgets()

        self.context.REQUEST.set('client', get_current_org_unit().id())
        searchableText = self.widgets["searchableText"]
        searchableText.value = self.request.get('SearchableText')

        for k, v in self.field_mapping().items():
            for name in v:
                if self.widgets.get(name, None):
                    self.widgets.get(name, None).addClass(k)

        self.set_object_provides_field_description()

    def set_object_provides_field_description(self):
        # set special description for object_provides field,
        # if the current setup is a multiclient_setup
        type_field = self.widgets.get('object_provides').field
        service = ogds_service()

        if service.has_multiple_admin_units():
            type_field.description = _(
                'help_portal_type_multiclient_setup',
                default='Select the contenttype to be searched for.'
                'It searches only items from the current client.')
        else:
            type_field.description = _(
                'help_portal_type',
                default='Select the contenttype to be searched for.')

    def get_field_mapping_for_interface(self, interface_name):
        interface_name = interface_name.replace('.', '-')
        return self.field_mapping().get(interface_name, [])

    def get_key_for_field_name(self, field_name):
        """Some fields need a new key in the upcoming request to @@search."""

        if field_name in ('task_review_state', 'dossier_review_state'):
            return 'review_state'
        return field_name

    def append_field_to_params(self, data, field_name, params):
        value = data.get(field_name, None)
        if not value:
            return

        key = self.get_key_for_field_name(field_name)

        if isinstance(value, date):
            self.append_date_field_to_params(data, field_name, params)
        elif isinstance(value, list):
            self.append_list_field_to_params(key, value, params)
        elif field_name == 'trashed':
            self.append_trashed_to_params(params)
        elif isinstance(value, int):
            self.append_sequence_number_to_params(value, params)
        else:
            self.append_key_to_params(key, value, params)

    def append_key_to_params(self, key, value, params):
        params.append((key, strip_parantheses(value.encode('utf-8'))))

    def append_sequence_number_to_params(self, value, params):
        params.append(('sequence_number:int', value))

    def append_trashed_to_params(self, params):
        params.append(('trashed:list:boolean', 'True'))
        params.append(('trashed:list:boolean', 'False'))

    def append_list_field_to_params(self, key, value, params):
        for list_value in value:
            params.append(
                ('{}:list'.format(key), list_value.encode('utf-8'))
            )

    def append_date_field_to_params(self, data, field_name, params):
        """Append a date field to the query parameters and handle date-ranges.

        A date it might be a composite of two values to filter a range. It
        might be one date only to filter a minimum or maximum date only.

        In case of a date-range we handle both values at once and drop them
        from data when we see the first entry.

        """
        base_field_name = field_name[:-2]
        field_1_name = "{}_1".format(base_field_name)
        field_2_name = "{}_2".format(base_field_name)

        field_1_value = data.pop(field_1_name, None)
        field_2_value = data.pop(field_2_name, None)

        if field_1_value and field_2_value:
            usage = 'minmax'
        elif field_1_value:
            usage = 'min'
        elif field_2_value:
            usage = 'max'
        params.append(('{}.range:record'.format(base_field_name), usage))

        key = '{}.query:record:list:date'.format(base_field_name)
        if field_1_value:
            params.append((key, field_1_value.strftime('%Y-%m-%d')))
        if field_2_value:
            inclusive_end_date = field_2_value + timedelta(days=1)
            params.append((key, inclusive_end_date.strftime('%Y-%m-%d')))

    def build_search_params(self, data):
        # cannot use dict since the same parameter key might be used repeatedly
        params = []

        object_provides = data.get('object_provides', '')
        params.append(('object_provides', object_provides))
        # if clause because it entered a searchableText=none without text
        if data.get('searchableText'):
            params.append(('SearchableText',
                           data.get('searchableText').encode('utf-8')))

        for field_name in self.get_field_mapping_for_interface(object_provides):
            self.append_field_to_params(data, field_name, params)

        return params

    @button.buttonAndHandler(_(u'button_search', default=u'Search'))
    def search(self, action):
        data, errors = self.extractData()
        if not errors:
            params = self.build_search_params(data)
            url = "{}/@@search?{}".format(self.context.portal_url(),
                                          urllib.urlencode(params))
            return self.context.REQUEST.RESPONSE.redirect(url)

import urllib
from five import grok
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as PMF
from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from z3c.form import button, field
from z3c.form.interfaces import INPUT_MODE
from z3c.form.browser import radio, checkbox
from plone.directives import form as directives_form
from opengever.advancedsearch import _
from opengever.ogds.base.autocomplete_widget import AutocompleteFieldWidget
from opengever.ogds.base.utils import get_client_id
from opengever.task.util import getTaskTypeVocabulary
from datetime import date
from ftw.datepicker.widget import DatePickerFieldWidget
from datetime import timedelta
import datetime
from zope.interface import Interface
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import re

@grok.provider(IContextSourceBinder)
def get_possible_dossier_states(context):
    wftool = getToolByName(context, 'portal_workflow')
    chain = wftool.getChainForPortalType(
        'opengever.dossier.businesscasedossier')[0]
    states = []
    for state in wftool.get(chain).states:
        states.append(SimpleVocabulary.createTerm(state, state, PMF(state)))
    return SimpleVocabulary(states)

@grok.provider(IContextSourceBinder)
def get_possible_task_states(context):
    wftool = getToolByName(context, 'portal_workflow')
    chain = wftool.getChainForPortalType(
        'opengever.task.task')[0]
    states = []
    for state in wftool.get(chain).states:
        states.append(SimpleVocabulary.createTerm(state, state, PMF(state)))
    return SimpleVocabulary(states)

@grok.provider(IContextSourceBinder)
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
        'opengever.document.document.IDocumentSchema',
        'opengever.document.document.IDocumentSchema',
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
                    'filing_no',
                    'responsible',
                    'dossier_review_state',
                ],
                'opengever-task-task-ITask':[
                    'issuer',
                    'deadline_1',
                    'deadline_2',
                    'task_type',
                    'task_review_state',
                ],
                'opengever-document-document-IDocumentSchema':[
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


class IAdvancedSearch(directives_form.Schema):

    searchableText = schema.TextLine(
        title=_('label_searchable_text', default='Text'),
        description=_('help_searchable_text', default=''),
        required=False,
    )

    object_provides = schema.Choice(
        title=_('label_portal_type', default="Type"),
        description=_('help_portal_type', default=''),
        source= get_types,
        required=True,
    )

    ### Dossier
    start_1 = schema.Date(
        title=_('label_start', default='Start date'),
        description=_('help_start', default=''),
        required=False,
    )

    start_2 = schema.Date(
        title=_('label_start_1', default=''),
        description=_('help_start_1', default=''),
        required=False,
    )

    end_1 = schema.Date(
        title=_('label_end', default='End date'),
        description=_('help_end', default=''),
        required=False,
    )

    end_2 = schema.Date(
        title=_('label_end_2', default=''),
        description=_('help_end_2', default=''),
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

    filing_no = schema.TextLine(
        title=_('label_filing_number', default='Filing number'),
        description=_('help_filing_number', default=''),
        required=False,
    )

    directives_form.widget(responsible=AutocompleteFieldWidget)
    responsible = schema.Choice(
        title=_('label_reponsible', default='Responsible'),
        description=_('help_responsible', default=''),
        vocabulary=u'opengever.ogds.base.AssignedUsersVocabulary',
        required=False,
    )

    dossier_review_state = schema.List(
        title=_('label_review_state', default='State'),
        description=_('help_review_state', default=''),
        value_type=schema.Choice(
            source=get_possible_dossier_states,
        ),
        required=False,
    )

    ### Document
    receipt_date_1 = schema.Date(
        title=_('label_receipt_date', default='Receipt date'),
        description=_('help_receipt_date', default=''),
        required=False,
    )

    receipt_date_2 = schema.Date(
        title=_('label_receipt_date_2', default=''),
        description=_('help_receipt_date_2', default=''),
        required=False,
    )

    delivery_date_1 = schema.Date(
        title=_('label_delivery_date', default='delivery date'),
        description=_('help_delivery_date', default=''),
        required=False,
    )

    delivery_date_2 = schema.Date(
        title=_('label_delivery_date_2', default=''),
        description=_('help_delivery_date_2', default=''),
        required=False,
    )

    document_date_1 = schema.Date(
        title=_('label_document_date', default='Document Date'),
        description=_('help_document_date', default=''),
        required=False,
    )

    document_date_2 = schema.Date(
        title=_('label_document_date_2', default=''),
        description=_('help_document_date_2', default=''),
        required=False,
    )

    document_author = schema.TextLine(
        title=_('label_document_author', default='Document author'),
        description=_('help_document_author', default=''),
        required=False,
    )

    directives_form.widget(responsible=AutocompleteFieldWidget)
    checked_out = schema.Choice(
        title=_('label_checked_out', default='Checked out by'),
        description=_('help_checked_out', default=''),
        vocabulary=u'opengever.ogds.base.UsersVocabulary',
        required=False,
    )

    trashed = schema.Bool(
        title=_('label_trashed', default='Also search in the recycle bin'),
        description=_('help_trashed', default=''),
        required=False,
    )

    ### Task
    directives_form.widget(issuer=AutocompleteFieldWidget)
    issuer = schema.Choice(
        title =_(u"label_issuer", default=u"Issuer"),
        description = _('help_issuer', default=u""),
        vocabulary=u'opengever.ogds.base.ContactsAndUsersVocabulary',
        required = False,
    )

    deadline_1 = schema.Date(
        title=_('label_deadline', default='Deadline'),
        description=_('help_start', default=''),
        required=False,
    )

    deadline_2 = schema.Date(
        title=_('label_deadline_2', default=''),
        description=_('help_deadline', default=''),
        required=False,
    )

    task_type = schema.Choice(
        title=_('label_tasktype', default=''),
        description=_('help_tasktyp', default=''),
        source=getTaskTypeVocabulary,
        required=False,
    )
    task_review_state = schema.List(
        title=_('label_review_state', default='State'),
        description=_('help_review_state', default=''),
        value_type=schema.Choice(
            source=get_possible_task_states,
        ),
        required=False,
    )

class AdvancedSearchForm(directives_form.Form):
    grok.context(Interface)
    grok.name('advanced_search')
    grok.require('zope2.View')

    label = _('advanced_search', default='advanced search')

    fields = field.Fields(IAdvancedSearch)
    fields['responsible'].widgetFactory[INPUT_MODE] \
        = AutocompleteFieldWidget
    fields['checked_out'].widgetFactory[INPUT_MODE] \
        = AutocompleteFieldWidget
    fields['issuer'].widgetFactory[INPUT_MODE] \
        = AutocompleteFieldWidget
    fields['object_provides'].widgetFactory[INPUT_MODE] \
        =  radio.RadioFieldWidget
    fields['dossier_review_state'].widgetFactory[INPUT_MODE] \
        = checkbox.CheckBoxFieldWidget
    fields['task_review_state'].widgetFactory[INPUT_MODE] \
        = checkbox.CheckBoxFieldWidget

    ignoreContext = True

    def updateWidgets(self):
        self.context.REQUEST.set('client', get_client_id())
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
            self.fields.get(field).widgetFactory[INPUT_MODE] = DatePickerFieldWidget

        super(AdvancedSearchForm, self).updateWidgets()
        for k,v in FIELD_MAPPING.items():
            for name in v:
                if self.widgets.get(name, None):
                    self.widgets.get(name, None).addClass(k)

    @button.buttonAndHandler(_(u'button_search', default=u'Search'))
    def search(self, action):
        data, errors = self.extractData()

        if not errors:
            # create Parameters and url
            if(data['reference']):
                data['reference'] = self.correct_ref(data['reference'])
            params = '/search?object_provides=%s' % (urllib.quote(data.get('object_provides', '')))
            # if clause because it entered a searchableText=none without text
            if data.get('searchableText'):
                params = '%s&SearchableText=%s' % (params, data.get('searchableText').encode('utf-8'))

            for field in FIELD_MAPPING.get(
                    data.get('object_provides').replace('.','-')):
                if data.get(field, None):
                    if isinstance(data.get(field), date):
                        if '1' in field:
                            params = '%s&%s_usage=range:minmax' % (params, field[:-2])
                            if not data.get(field[:-2]+'_2'):
                                data[field[:-2]+'_2'] = datetime.date(2020, 12, 30)
                        else:
                            if not data.get(field[:-2]+'_1'):
                                params = '%s&%s_usage=range:minmax' % (params, field[:-2])
                                data[field[:-2]+'_1'] = datetime.date(1900, 1, 1)
                                params = '%s&%s:list=%s' % (params, field[:-2], data.get(field[:-2]+'_1').strftime('%m/%d/%y'))
                            data[field] = data.get(field) + timedelta(1)
                        params = '%s&%s:list=%s' % (params, field[:-2], data.get(field).strftime('%m/%d/%y'))

                    elif isinstance(data.get(field), list):
                        for value in data.get(field):
                            params = '%s&%s:list=%s' % (params, field, value.encode('utf-8'))
                    elif field == 'trashed':
                        params = '%s&trashed:list:boolean=True&trashed:list:boolean=False' %(params)
                    elif isinstance(data.get(field), int):
                        params = '%s&sequence_number:int=%s' %(params, data.get(field))
                    else:
                        params = '%s&%s=%s' %(params, field, urllib.quote(data.get(field).encode('utf-8')))

            params = params.replace('task_review_state', 'review_state')
            params = params.replace('dossier_review_state', 'review_state')

            self.context.REQUEST.RESPONSE.redirect(self.context.portal_url() + params)


    def correct_ref(self, value):
        registry = getUtility(IRegistry)
        prefix = registry['opengever.base.interfaces.IBaseClientID.client_id']
        if prefix.lower() in value.lower():
            value = value.replace(prefix, "")
            value = value.replace(prefix.lower(), "")
        refnr = re.split('[^a-zA-Z0-9\.]', value)
        while refnr.count(''):
            refnr.remove('')
        value = ' / '.join(refnr)
        return prefix + " " +value

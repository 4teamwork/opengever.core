from Acquisition import aq_inner, aq_parent
from opengever.dossier import _
from ftw.task import util
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from zope import schema
from zope.interface import Interface, alsoProvides
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from plone.indexer import indexer
from five import grok
from datetime import datetime
from zope.interface import invariant, Invalid


class IDossierMarker(Interface):
    """ Marker Interface for dossiers.
    """

class IDossier(form.Schema):
    """ Behaviour interface for dossier types providing common properties/fields.
    """

    form.fieldset(
        u'common',
        fields = [
                u'keywords',
                u'start',
                u'end',
                u'volume_number',
                u'comments',
                u'responsible',
        ],
    )
    
    keywords = schema.Tuple(
        title = _(u'label_keywords', default=u'Keywords'),
        description = _(u'help_keywords', default=u''),
        value_type = schema.TextLine(),
        required = False,
        missing_value = (),
        )
    form.widget(keywords = TextLinesFieldWidget)

        
    form.widget(start='ftw.datepicker.widget.DatePickerFieldWidget')
    #form.widget(start=DateTimePickerFieldWidget)
    #form.widget(start='collective.z3cform.datepicker.widget.DatePickerFieldWidget')
    start = schema.Date(
        title=_(u'label_start', default=u'Opening Date'),
        description = _(u'help_start', default=u''), 
        required=False,
    )

    form.widget(end='ftw.datepicker.widget.DatePickerFieldWidget')
    #form.widget(end=DateTimePickerFieldWidget)
    #form.widget(end='collective.z3cform.datepicker.widget.DatePickerFieldWidget')
    end = schema.Date(
        title=_(u'label_end', default=u'Closing Date'),
        description = _(u'help_end', default=u''),   
        required=False,
    )
    
    volume_number = schema.TextLine(
        title = _(u'label_volume_number', default=u'Volume Number'),
        description = _(u'help_volume_number', default=u''),
        required=False,
    )
        
    comments = schema.Text(
        title=_(u'label_comments', default=u'Comments'),
        description = _(u'help_comments', default=u''),    
        required=False
    )
    
    form.widget(responsible=AutocompleteFieldWidget)
    responsible = schema.Choice(
        title=_(u"label_responsible", default="Responsible"),
        description =_(u"help_responsible", default="select an responsible Manger"),
        source = util.getManagersVocab,
        required = True,
    )

    form.fieldset(
        u'filing',
        label = _(u'fieldset_filing', default=u'Filing'),
        fields = [
                u'container_type',
                u'container_id',
                u'number_of_containers',
                u'container_location',
        ],
    )

    container_type = schema.Choice(
        title = _(u'label_container_type', default=u'Container Type'),
        description = _(u'help_container_type', default=u''),
        source = u'classification_classification_vocabulary',
        required = False,
    )
    
    container_id = schema.TextLine(
        title = _(u'label_container_id', default=u'Container Id'),
        description = _(u'help_container_id', default=u''),
        required = False,
    )
    
    number_of_containers = schema.Int(
        title = _(u'label_number_of_containers', default=u'Number of Containers'),
        description = _(u'help_number_of_containers', default=u''),
        required = False,
    )        

    container_location = schema.TextLine(
        title = _(u'label_container_location', default=u'Container Location'),
        description = _(u'help_container_location', default=u''),
        required = False,
    )
    @invariant
    def validateStartEnd(data):
        if data.start is not None and data.end is not None:
            if data.start > data.end:
                raise StartBeforeEnd

alsoProvides(IDossier, IFormFieldProvider)

class StartBeforeEnd(Invalid):
     __doc__ = _(u"The start or end date is invalid")
# 
# StartBeforeEndMessage = error.ErrorViewMessage(u"The start date must be before the end date.",error=StartBeforeEnd)
# provideAdapter(StartBeforeEndMessage,name="message")

#startBeforeEndError = StartBeforeEnd(u'The start date must be before the end date')
#errorView = error.InvalidErrorViewSnippet(startBeforeEndError, None, None, None, None, None)
#provideAdapter(errorView)

# XXX testing widget attributes
# 
# import grokcore.component
# from z3c.form.widget import StaticWidgetAttribute
# 
# rows_override = StaticWidgetAttribute(u'blablabla', field=IDossier['comments'])
# grok.global_adapter(rows_override, name=u"value")
# labelOverride = StaticWidgetAttribute(u"Override label2", field=IDossier['comments'])
# grok.global_adapter(labelOverride, name=u"label")
# #import pdb; pdb.set_trace()
# testOverride = StaticWidgetAttribute(True, field=IDossier['volume_number'])
# grok.global_adapter(testOverride, name=u"required")

@form.default_value(field=IDossier['start'])
def deadlineDefaultValue(data):
    return datetime.today()

@indexer(IDossierMarker)
def startIndexer(obj):
    aobj = IDossier(obj)
    if aobj.start is None:
        return None
    return aobj.start
grok.global_adapter(startIndexer, name="start") 

@indexer(IDossierMarker)
def endIndexer(obj):
    aobj = IDossier(obj)
    if aobj.end is None:
        return None
    return aobj.end
grok.global_adapter(endIndexer, name="end")

@indexer(IDossierMarker)
def responsibleIndexer(obj):
    aobj = IDossier(obj)
    if aobj.responsible is None:
        return None
    return aobj.responsible
grok.global_adapter(responsibleIndexer, name="responsible")

@indexer(IDossierMarker)
def isSubdossierIndexer(obj):
    parent = aq_parent(aq_inner(obj))
    if IDossierMarker.providedBy(parent):
        return True
    return False
grok.global_adapter(isSubdossierIndexer, name="is_subdossier")

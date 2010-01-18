import logging

from five import grok
from datetime import datetime
from Acquisition import aq_inner, aq_parent
from opengever.dossier import _
from ftw.task import util
from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError

from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from plone.indexer import indexer
from plone.namedfile.interfaces import INamedFileField
from plone.registry.interfaces import IRegistry
from plone.app.dexterity.behaviors.metadata import IBasic

from zope.interface import invariant, Invalid
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IContextSourceBinder
from zope import schema
from zope.interface import Interface, alsoProvides
from zope.component import queryUtility

from opengever.dossier.interfaces import IDossierContainerTypes

from z3c.relationfield.schema import RelationChoice, RelationList
from plone.formwidget.contenttree import ObjPathSourceBinder

LOG = logging.getLogger('opengever.dossier')

@grok.provider(IContextSourceBinder)
def container_types(context):
    voc= []
    terms = []
    registry = queryUtility(IRegistry)
    proxy = registry.forInterface(IDossierContainerTypes)
    voc = getattr(proxy, 'container_types')
    for term in voc:
        terms.append(SimpleVocabulary.createTerm(term))
    return SimpleVocabulary(terms)

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
                u'comments',
                u'responsible',
                u'relatedDossier',
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
                u'volume_number',
                u'number_of_containers',
                u'container_location',
        ],
    )

    container_type = schema.Choice(
        title = _(u'label_container_type', default=u'Container Type'),
        description = _(u'help_container_type', default=u''),
        source = container_types,
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
    
    relatedDossier = RelationList(
        title=_(u'label_related_dossier', default=u'Related Dossier'),
        default=[],
        value_type=RelationChoice(title=u"Related",
                   source=ObjPathSourceBinder(navigation_tree_query={'object_provides' : ('opengever.dossier.behaviors.dossier.IDossierMarker',),})),
        required=False,
        )
            
    @invariant
    def validateStartEnd(data):
        if data.start is not None and data.end is not None:
            if data.start > data.end:
                raise StartBeforeEnd(_(u"The start date must be before the end date."))

alsoProvides(IDossier, IFormFieldProvider)


class StartBeforeEnd(Invalid):
    __doc__ = _(u"The start or end date is invalid")


# XXX testing widget attributes
# 
# import grokcore.component
# from z3c.form.widget import StaticWidgetAttribute
# 
# rows_override = StaticWidgetAttribute(u'blablabla', field=IDossier['comments'])
# grok.global_adapter(rows_override, name=u"value")
# labelOverride = StaticWidgetAttribute(u"Override label2", field=IDossier['comments'])
# grok.global_adapter(labelOverride, name=u"label")
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

# INDEX: SearchableText
@indexer(IDossierMarker)
def SearchableText(obj):
    context = aq_inner(obj)
    transforms = getToolByName(obj, 'portal_transforms')
    fields = [
        schema.getFields(IBasic).get('title'),
        schema.getFields(IBasic).get('description'),
        schema.getFields(IDossier).get('keywords'),
        ]
    searchable = []
    for field in fields:
        try:
            data = field.get(context)
        except AttributeError:
            data = field.get(field.interface(context))
        if not data:
            continue
        if INamedFileField.providedBy(field):
            # we need to convert the file data to string, so we can
            # index it
            datastream = ''
            try:
                datastream = transforms.convertTo(
                    "text/plain",
                    data.data,
                    mimetype = data.contentType,
                    filename = data.filename,
                    )
            except (ConflictError, KeyboardInterrupt):
                raise
            except Exception, e:
                LOG.error("Error while trying to convert file contents to 'text/plain' "
                          "in SearchableIndex(dossier.py): %s" % (e,))
            data = str(datastream)
        if isinstance(data, unicode):
            data = data.encode('utf8')
        if isinstance(data, tuple) or isinstance(data, list):
            data = " ".join([str(a) for a in data])
        if data:
            searchable.append(data)
    return ' '.join(searchable)
grok.global_adapter(SearchableText, name='SearchableText')

from opengever.dossier import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from zope import schema
from zope.interface import alsoProvides
#from collective.z3cform.datetimewidget.widget import DateWidget
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.z3cform.textlines.textlines import TextLinesFieldWidget

class IDossier(IBasic):
    """ Behaviour interface for dossier types providing common properties/fields.
    """

    form.fieldset(
        u'common',
        label = _(u'fieldset_common', default=u'Common'),
        fields = [
                u'title',
                u'description',
                u'keywords',
                u'start',
                u'end',
                u'volume_number',
                u'comments',
        ],
    )
    
    form.order_before(description = '*')
    form.order_before(title = '*')

    keywords = schema.Tuple(
        title = _(u'label_keywords', default=u'Keywords'),
        description = _(u'help_keywords', default=u''),
        value_type = schema.TextLine(),
        required = False,
        missing_value = (),
        )
    form.widget(keywords = TextLinesFieldWidget)
        

    #form.widget(start=DateTimePickerFieldWidget)
    #form.widget(start=DateWidget)
    start = schema.Date(
        title=_(u'label_start', default=u'Opening Date'),
        description = _(u'help_start', default=u''), 
        required=False,
    )

    #form.widget(end=DateTimePickerFieldWidget)
    #form.widget(end=DateWidget)
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
        
alsoProvides(IDossier, IFormFieldProvider)
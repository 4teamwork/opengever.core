from opengever.dossier import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from zope import schema
from zope.interface import alsoProvides
from collective.z3cform.datetimewidget.widget import DateWidget

class IDossier(form.Schema):
    """ Behaviour interface for dossier types providing common properties/fields.
    """

    #form.widget(start=DateTimePickerFieldWidget)
    #form.widget(start=DateWidget)
    start = schema.Date(
            title=_(u"Dossier Opening Date"),
            required=False,
    )

    #form.widget(end=DateTimePickerFieldWidget)
    #form.widget(end=DateWidget)
    end = schema.Date(
            title=_(u"Dossier Closing Date"),
            required=False,
    )
        
    comment = schema.Text(
            title=_(u"Comment"),
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
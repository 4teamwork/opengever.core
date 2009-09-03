from opengever.dossier import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from zope import schema
from zope.interface import alsoProvides


class IDossier(form.Schema):
    """ Behaviour interface for dossier types providing common properties/fields.
    """

    #form.widget(start=DateTimePickerFieldWidget)
    #form.widget(start=DateWidget)
    start = schema.Datetime(
            title=_(u"Dossier Opening Date"),
            required=False,
    )

    #form.widget(end=DateTimePickerFieldWidget)
    #form.widget(end=DateWidget)
    end = schema.Datetime(
            title=_(u"Dossier Closing Date"),
            required=False,
    )
        
    comment = schema.Text(
            title=_(u"Comment"),
            required=False
    )
    
alsoProvides(IDossier, IFormFieldProvider)
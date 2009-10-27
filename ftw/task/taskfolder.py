from five import grok
from zope import schema

from plone.directives import form, dexterity

from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage

from ftw.task import _

class ITaskFolder(form.Schema):
    
    title = schema.TextLine(
        title=_(u"title", default=u"Title"),
        description=_(u"descTitle", default=u"Enter a short, descriptive title for the issue. A good title will make it easier for project managers to identify and respond to the issue."),        
        required = True,
    )
    
    text = schema.Text(
        title=_(u"text", default=u"Text"),
        description=_(u"descText", default=u"Enter all your Angaben"),
        required = True,
    )

    deadline = schema.Datetime(
        title=_(u"deadline", default=u"Deadline"),
        required = False, 
    )
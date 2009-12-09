from plone.directives import form
from plone.directives import dexterity
from five import grok
from Products.CMFCore.utils import getToolByName

class IInbox(form.Schema):
    """ Inbox for OpenGever
    """
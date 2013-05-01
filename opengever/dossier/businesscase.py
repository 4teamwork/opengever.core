from five import grok

from plone.directives import form
from plone.directives import dexterity


class IBusinessCaseDossier(form.Schema):
    """ A business case dossier
    """


class View(dexterity.DisplayForm):
    grok.context(IBusinessCaseDossier)
    grok.require('zope2.View')

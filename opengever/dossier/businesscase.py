
from zope import schema
from zope.interface import implements, invariant, Invalid

from plone.dexterity import content
from plone.directives import form
from plone.directives import dexterity
from plone.app.dexterity.behaviors import metadata


class IBusinessCaseDossier(form.Schema):
    """ A business case dossier
    """

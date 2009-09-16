
from zope import schema
from zope.interface import implements, invariant, Invalid

from plone.dexterity import content
from plone.directives import form
from plone.directives import dexterity
from plone.app.dexterity.behaviors import metadata


class IProjectDossier(form.Schema):
    """ A project dossier
    """

    # just an example field for a project dossier
    project_manager = schema.TextLine(
            title = u'Project Manager',
            required = False
    )

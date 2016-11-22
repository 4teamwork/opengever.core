from opengever.dossier.behaviors.dossiernamefromtitle import DossierNameFromTitle
from plone.app.content.interfaces import INameFromTitle
from plone.directives import form
from zope.interface import implements


class IDossierTemplate(form.Schema):
    """Behaviour interface for dossier template types.

    Use this type of dossier to create a reusable template structures.
    """


class IDossierTemplateNameFromTitle(INameFromTitle):
    """Behavior interface.
    """


class DossierTemplateNameFromTitle(DossierNameFromTitle):
    """Choose IDs for a dossiertemplate in the following format:
    'dossiertemplate-{sequence number}'
    """

    implements(IDossierTemplateNameFromTitle)

    format = u'dossiertemplate-%i'

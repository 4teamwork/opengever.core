from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossiernamefromtitle import DossierNameFromTitle
from plone.app.content.interfaces import INameFromTitle
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.interface import implements


class IDossierTemplateSchema(form.Schema):
    """Schema interface for dossier template types.

    Use this type of dossier to create a reusable template structures.
    """


class IDossierTemplateMarker(Interface):
    """Marker Interface for dossiertemplates.
    """


class IDossierTemplate(IDossier):
    """Behavior Interface for dossiertemplates.

    We need the IDossier behavior fields for the dossier template.
    Unfortunately we cannot use the IDossier behavior directly because
    it's providing the IDossierMarker interface which will destroy
    some functionality of the dossiertemplate.

    To fix that, we have to create a subclass of the IDosser behavior
    and register it with an own IDossierTemplateMarker interface.

    With this workaround we get the schema of the IDossier but
    not its marker interfaces.
    """

alsoProvides(IDossierTemplate, IFormFieldProvider)


class IDossierTemplateNameFromTitle(INameFromTitle):
    """Behavior interface.
    """


class DossierTemplateNameFromTitle(DossierNameFromTitle):
    """Choose IDs for a dossiertemplate in the following format:
    'dossiertemplate-{sequence number}'
    """

    implements(IDossierTemplateNameFromTitle)

    format = u'dossiertemplate-%i'

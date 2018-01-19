from opengever.base.interfaces import IReferenceNumberFormatter
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.dossier.base import DossierContainer
from opengever.dossier.businesscase import IBusinessCaseDossier
from opengever.private.interfaces import IPrivateContainer
from plone import api
from zope.component import queryAdapter


class IPrivateDossier(IBusinessCaseDossier, IPrivateContainer):
    """PrivateDossier marker interface.
    """


class PrivateDossier(DossierContainer):
    """A specific dossier type, only addable to a PrivateFolder in the
    private Area and only visible for the Owner and Managers.
    """

    def get_reference_number(self):
        """Prefix reference numbers of private dossiers with a 'P'."""
        active_formatter_name = api.portal.get_registry_record(
            name='formatter',
            interface=IReferenceNumberSettings,
            )

        formatter = queryAdapter(
            api.portal.get(),
            IReferenceNumberFormatter,
            name=active_formatter_name,
            )

        separator = getattr(formatter, 'repository_dossier_separator', u' ')

        return separator.join((
            'P',
            super(PrivateDossier, self).get_reference_number(),
            ))

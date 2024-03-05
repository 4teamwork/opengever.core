from copy import deepcopy
from opengever.base.menu import FilteredPostFactoryMenuWithWebactions
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.ris import RIS_VIEW_ADD_PROPOSAL
from opengever.ris.interfaces import IRisSettings
from plone import api
from zope.component import adapter
from zope.interface import Interface


@adapter(IDossierMarker, Interface)
class DossierPostFactoryMenu(FilteredPostFactoryMenuWithWebactions):

    dossier_types = [u'opengever.dossier.businesscasedossier',
                     u'opengever.private.dossier']

    def __init__(self, context, request):
        super(DossierPostFactoryMenu, self).__init__(context, request)

    def __call__(self, factories):
        factories = super(DossierPostFactoryMenu, self).__call__(factories)
        manager_factories = []
        for factory in factories:
            if factory.get('id') == u"opengever.ris.proposal":
                # keep original add menu factory for `Manager` debugging
                if api.user.has_permission('Manage portal'):
                    manager_factory = deepcopy(factory)
                    manager_factory['title'] = _(u"Proposal (Manager: Debug)")
                    manager_factories.append(manager_factory)

                # point default add menu factory to Ris
                ris_url = api.portal.get_registry_record(
                    name='base_url', interface=IRisSettings
                ).rstrip("/")
                ris_add_url = '{}/{}?context={}'.format(
                    ris_url,
                    RIS_VIEW_ADD_PROPOSAL,
                    self.context.absolute_url(),
                )
                factory['action'] = ris_add_url

        factories.extend(manager_factories)
        return factories

    def rename(self, factory):
        if factory.get('id') in self.dossier_types:
            factory['title'] = _(u'Subdossier')

        return factory

    def is_filtered(self, factory):
        factory_id = factory.get('id')
        if factory_id == u'ftw.mail.mail':
            return True

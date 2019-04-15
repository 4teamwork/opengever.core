from opengever.base.menu import FilteredPostFactoryMenuWithWebactions
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossierMarker
from zope.component import adapter
from zope.interface import Interface


@adapter(IDossierMarker, Interface)
class DossierPostFactoryMenu(FilteredPostFactoryMenuWithWebactions):

    dossier_types = [u'opengever.dossier.businesscasedossier',
                     u'opengever.private.dossier']

    def __init__(self, context, request):
        super(DossierPostFactoryMenu, self).__init__(context, request)

    def rename(self, factory):
        if factory.get('id') in self.dossier_types:
            factory['title'] = _(u'Subdossier')

        return factory

    def is_filtered(self, factory):
        factory_id = factory.get('id')
        if factory_id == u'ftw.mail.mail':
            return True

from five import grok
from opengever.base.menu import FilteredPostFactoryMenu
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossierMarker
from zope.interface import Interface


class DossierPostFactoryMenu(FilteredPostFactoryMenu):
    grok.adapts(IDossierMarker, Interface)

    def is_filtered(self, factory):
        factory_id = factory.get('id')
        if factory_id == u'ftw.mail.mail':
            return True

        return False

    def __call__(self, factories):
        factories = super(DossierPostFactoryMenu, self).__call__(factories)
        for factory in factories:
            if factory.get('id') == u'opengever.dossier.businesscasedossier':
                factory['title'] = _(u'Subdossier')

        return factories

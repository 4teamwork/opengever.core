from five import grok
from opengever.base.menu import FilteredPostFactoryMenu
from opengever.dossier import _
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateSchema
from zope.interface import Interface


class DossierTemplatePostFactoryMenu(FilteredPostFactoryMenu):
    grok.adapts(IDossierTemplateSchema, Interface)

    subdossier_types = [u'opengever.dossier.dossiertemplate']

    def rename(self, factory):
        if factory.get('id') in self.subdossier_types:
            factory['title'] = _(u'Subdossier')

        return factory

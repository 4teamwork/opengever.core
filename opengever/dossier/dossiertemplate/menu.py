from opengever.base.menu import FilteredPostFactoryMenuWithWebactions
from opengever.dossier import _
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateSchema
from zope.component import adapter
from zope.interface import Interface


@adapter(IDossierTemplateSchema, Interface)
class DossierTemplatePostFactoryMenu(FilteredPostFactoryMenuWithWebactions):

    subdossier_types = [u'opengever.dossier.dossiertemplate']

    def rename(self, factory):
        if factory.get('id') in self.subdossier_types:
            factory['title'] = _(u'Subdossier')

        return factory

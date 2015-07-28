from ftw.upgrade import UpgradeStep
from zc.relation.interfaces import ICatalog
from zope.component import getUtility


TO_REMOVE = ['plone.directives.form.schema.Schema',
             'plone.app.kss.interfaces.IPortalObject']


class CleanupRelationsCatalog(UpgradeStep):

    def __call__(self):
        self.relations_catalog = getUtility(ICatalog)

        for iface_name in TO_REMOVE:
            self.cleanup_interface(iface_name, 'to_interfaces_flattened')
            self.cleanup_interface(iface_name, 'from_interfaces_flattened')

    def cleanup_interface(self, iface_name, mapping_key):
        for iface in self.relations_catalog._name_TO_mapping[mapping_key].keys():
            if '{}.{}'.format(iface.__module__, iface.__name__) == iface_name:
                del self.relations_catalog._name_TO_mapping[mapping_key][iface]
                break

from BTrees.check import check
from ftw.upgrade import UpgradeStep
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
import logging


logger = logging.getLogger('opengever.base')

TO_REMOVE = ['plone.directives.form.schema.Schema',
             'plone.app.kss.interfaces.IPortalObject']


class CleanupRelationsCatalog(UpgradeStep):

    def __call__(self):
        self.catalog = getUtility(ICatalog)

        for iface_name in TO_REMOVE:
            self.cleanup_to_mapping(iface_name, 'to_interfaces_flattened')
            self.cleanup_to_mapping(iface_name, 'from_interfaces_flattened')
            self.cleanup_objtokenset(
                ['from_interfaces_flattened', 'to_interfaces_flattened'])

    def cleanup_to_mapping(self, iface_name, mapping_key):
        # Check the BTree consistency, to avoid key errors when deleting
        # entries in the BTree.
        # If the check method detects an inconsistency, we fix the Btree by
        # creating a copy of it.
        #
        # See http://do3.cc/blog/2012/09/264/debugging-zcrelations---broken-btrees/
        # for more information.
        try:
            check(self.catalog._name_TO_mapping[mapping_key])
        except AssertionError:
            btree = self.catalog._name_TO_mapping[mapping_key]
            self.catalog._name_TO_mapping[mapping_key] = btree.__class__(btree)
            logger.warning(
                'Inconsistent BTree detected and fixed by recreating it.')

        for iface in self.catalog._name_TO_mapping[mapping_key].keys():
            if '{}.{}'.format(iface.__module__, iface.__name__) == iface_name:
                del self.catalog._name_TO_mapping[mapping_key][iface]
                break

    def cleanup_objtokenset(self, attribute_names):
        for (key, value) in self.catalog._reltoken_name_TO_objtokenset.items():
            token, name = key
            if name in attribute_names:
                broken_values = [iface for iface in value
                                 if '{}.{}'.format(iface.__module__, iface.__name__) in TO_REMOVE]

                for broken in broken_values:
                    value.remove(broken)

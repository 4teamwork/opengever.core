from ftw.upgrade import UpgradeStep
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
import cPickle
import logging
import StringIO


logger = logging.getLogger('opengever.core')

POTENTIALLY_BROKEN = ('to_interfaces_flattened', 'from_interfaces_flattened')


class FixRelationCatalogReferences(UpgradeStep):
    """Fix relation catalog references.

    This upgrade fixes an issue with btrees somehow still referencing the
    already removed ICreatorAware class.
    """

    def __call__(self):
        catalog = getUtility(ICatalog)

        for mapping_key in POTENTIALLY_BROKEN:
            btree = catalog._name_TO_mapping[mapping_key]
            if self.has_broken_references(btree):
                logger.warning(
                    'Broken references on BTree "{}" detected'
                    .format(mapping_key))
                catalog._name_TO_mapping[mapping_key] = btree.__class__(btree)

    def has_broken_references(self, btree):
        """If the btree contains broken references they will result in a
        pickling error, e.g:

        Can't pickle <class 'opengever.base.behaviors.creator.ICreatorAware'>:
        import of module opengever.base.behaviors.creator failed

        """
        pickler = cPickle.Pickler(StringIO.StringIO())
        try:
            pickler.dump(btree)
        except cPickle.PicklingError as e:
            return True

        return False

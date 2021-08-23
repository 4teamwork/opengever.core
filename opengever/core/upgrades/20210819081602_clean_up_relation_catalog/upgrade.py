from ftw.upgrade import UpgradeStep
from zc.relation.interfaces import ICatalog
from zope import component


class CleanUpRelationCatalog(UpgradeStep):
    """Clean up relation catalog.
    """

    deferrable = True

    def __call__(self):
        catalog = component.queryUtility(ICatalog)
        for relation in catalog:
            if relation.to_object is None:
                if not relation.isBroken():
                    relation.broken(None)
            if relation.from_object is None:
                catalog.unindex(relation)

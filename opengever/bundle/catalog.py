from Products.CMFCore.CMFCatalogAware import CMFCatalogAware


def indexObject(self):
    pass


def unindexObject(self):
    pass


def reindexObject(self, idxs=[]):
    pass


original_methods = {}


def disable_indexing():
    if not original_methods:
        original_methods.update({
            'index': CMFCatalogAware.indexObject,
            'reindex': CMFCatalogAware.reindexObject,
            'unindex': CMFCatalogAware.unindexObject,
        })
        CMFCatalogAware.indexObject = indexObject
        CMFCatalogAware.reindexObject = reindexObject
        CMFCatalogAware.unindexObject = unindexObject


def enable_indexing():
    if not original_methods:
        return
    CMFCatalogAware.indexObject = original_methods.pop('index')
    CMFCatalogAware.reindexObject = original_methods.pop('reindex')
    CMFCatalogAware.unindexObject = original_methods.pop('unindex')

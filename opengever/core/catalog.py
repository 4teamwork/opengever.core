from plone import api


def add_catalog_indexes(indexes, logger):
    """Add all `indexes` to the plone catalog and log progess in `logger`.

    The argument `indexes` can be a tuple of length two when only name and
    meta_type are required. It also supports a tuple of length three when
    additional arguments are required to add an index (e.g. when adding a
    `ZCTextIndex` index).

    """
    catalog = api.portal.get_tool('portal_catalog')
    current_indexes = catalog.indexes()

    indexables = []
    for index_meta in indexes:
        name, meta_type, args = _extract_index_arguments(index_meta)
        if name not in current_indexes:
            _add_catalog_index(name, meta_type, catalog, args)
            indexables.append(name)
            logger.info("Added %s for field %s.", meta_type, name)
    if len(indexables) > 0:
        logger.info("Indexing new indexes %s.", ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)


class _Extras(object):
    """Handles extra arguments for adding an index."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def _add_catalog_index(name, meta_type, catalog, args):
    if meta_type == 'ZCTextIndex':
        catalog.addIndex(name, meta_type, _Extras(**args))
    else:
        catalog.addIndex(name, meta_type)


def _extract_index_arguments(index_meta):
    name, meta_type = index_meta[:2]
    args = index_meta[2] if len(index_meta) == 3 else {}

    return name, meta_type, args

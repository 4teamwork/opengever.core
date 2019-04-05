from BTrees.IIBTree import IISet, intersection, union, difference
from opengever.base.monkey.patching import MonkeyPatch


class PatchExtendedPathIndex(MonkeyPatch):
    """Add support for excluding the root path."""

    def __call__(self):
        from Products.ExtendedPathIndex.ExtendedPathIndex import ExtendedPathIndex

        self.patch_value(
            ExtendedPathIndex,
            'query_options',
            ("query", "level", "operator", "depth", "navtree", "navtree_start",
             "exclude_root"),
        )

        def query_index(self, record, resultset=None):
            level = record.get("level", 0)
            operator = record.get('operator', self.useOperator).lower()
            depth = getattr(record, 'depth', -1)  # use getattr to get 0 value
            navtree = record.get('navtree', 0)
            navtree_start = record.get('navtree_start', 0)
            exclude_root = record.get('exclude_root', 0)

            # depending on the operator we use intersection of union
            if operator == "or":
                set_func = union
            else:
                set_func = intersection

            result = None
            for k in record.keys:
                rows = self.search(k, level, depth, navtree, navtree_start,
                                   resultset=resultset)
                if exclude_root:
                    root = self._index_items.get(k)
                    rows = difference(rows, root)
                result = set_func(result, rows)

            if result:
                return result
            return IISet()
        self.patch_refs(ExtendedPathIndex, 'query_index', query_index)

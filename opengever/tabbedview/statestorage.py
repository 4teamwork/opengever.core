from ftw.tabbedview.statestorage import DefaultGridStateStorageKeyGenerator
from opengever.tabbedview.interfaces import ITabbedViewProxy


class GeverGridStateStorageKeyGenerator(DefaultGridStateStorageKeyGenerator):

    def _append_view_name(self, key):
        view_name = self.tabview.__name__
        if ITabbedViewProxy.providedBy(self.tabview):
            view_name = self.tabview.name_without_postfix
        key.append(view_name)

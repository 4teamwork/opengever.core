from ftw.dictstorage.base import DictStorage
from opengever.tabbedview.interfaces import ITabbedViewProxy
from opengever.tabbedview.statestorage import GeverGridStateStorageKeyGenerator


class DossierGridStateStorageKeyGenerator(GeverGridStateStorageKeyGenerator):
    """This storage key generator creates a shared key for all dossier types,
    since we need to share the configuration between different dossier types.
    """

    def _append_portal_type(self, key):
        key.append("opengever.dossier")


class GeverTabbedviewDictStorage(DictStorage):
    """The tabbedview uses the view as context to
    get and store the tabbedview-state.

    For the normal use, this works properly.

    Since the bumblebee-integration we need a special case.

    We have a proxy view which defines if the list or gallery
    shoud be displayed. So we have a master-view for two subviews.

    If the tabbedview will get the state while viewing a tab,
    it will call the DictStorage with the subview as the context.

    If it wants to store a new state, the tabbedview calls
    the DictStorage with the master-view.

    So we don't have the same config while storing and getting
    the state.

    To handle this, we have to change the accesskey and the
    context to the subview.
    """

    def __init__(self, context):
        context = self.change_proxy_context(context)
        super(GeverTabbedviewDictStorage, self).__init__(context)

    def __getitem__(self, key, default=None):
        key = self.strip_proxy_postfix(self.context, key)
        return super(GeverTabbedviewDictStorage, self).__getitem__(key, default)

    def __setitem__(self, key, value):
        key = self.strip_proxy_postfix(self.context, key)
        return super(GeverTabbedviewDictStorage, self).__setitem__(key, value)

    def __delitem__(self, key):
        key = self.strip_proxy_postfix(self.context, key)
        return super(GeverTabbedviewDictStorage, self).__setitem__(key)

    def strip_proxy_postfix(self, view, value):
        if ITabbedViewProxy.providedBy(view):
            value = view.name_without_postfix
        return value

    def change_proxy_context(self, view):
        if ITabbedViewProxy.providedBy(view):
            non_proxy_view_name = self.strip_proxy_postfix(view, view.__name__)
            view = view.context.restrictedTraverse(non_proxy_view_name)

        return view

    get = __getitem__
    set = __setitem__

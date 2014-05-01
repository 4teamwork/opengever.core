from five import grok
from opengever.repository.interfaces import IRepositoryFolder
from plone.memoize.interfaces import ICacheChooser
from zope.component import queryUtility
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


@grok.subscribe(IRepositoryFolder, IObjectModifiedEvent)
def invalidate_repository_cache(folder, event):
    """The contents of the TreeView portlet get cached in ftw.treeview.
    Upon changes to any of the RepositoryFolders we need to invalidate this
    cache.
    """
    chooser = queryUtility(ICacheChooser)
    if chooser is not None:
        cache = chooser('ftw.treeview.view.get_tree')
        cache.ramcache.invalidate('ftw.treeview.view.get_tree')

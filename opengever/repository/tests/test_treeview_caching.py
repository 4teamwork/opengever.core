from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class TestTreeviewCacheInvalidation(FunctionalTestCase):

    def test_modifying_repo_folder_invalidates_treeview_cache(self):
        """Changing a repo folder should invalidate the cache for the
        contents of the TreeView portlet.
        See opengever/repository/handlers.py
        """
        repository = create(Builder('repository_root'))
        repo_folder = create(Builder('repository')
                             .within(repository)
                             .having(effective_title="Foo"))

        tree_view = repository.restrictedTraverse('tree')

        # Test initial title of our repo folder
        html = tree_view.render()
        self.assertIn('1. Foo', html)

        # Now modify the repo folder and fire ObjectModified.
        # Changes should reflect in the output of the TreeView portlet
        repo_folder.effective_title = 'Bar'
        notify(ObjectModifiedEvent(repo_folder))
        html = tree_view.render()
        self.assertIn('1. Bar', html)

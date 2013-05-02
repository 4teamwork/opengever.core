import unittest2 as unittest
from opengever.dossier.testing import OPENGEVER_DOSSIER_INTEGRATION_TESTING
from plone.dexterity.utils import createContentInContainer

class TestMoveItemsIntegration(unittest.TestCase):

    layer = OPENGEVER_DOSSIER_INTEGRATION_TESTING

    def test_integration(self):
        """ Test integration of move_items method
        """
        portal = self.layer['portal']
        request = self.layer['request']

        # Create dummycontent
        repo1 = portal[portal.invokeFactory(
            'opengever.repository.repositoryfolder', 'repo1')]
        repo2 = portal[portal.invokeFactory(
            'opengever.repository.repositoryfolder', 'repo2')]

        dossier1 = repo1[repo1.invokeFactory(
            'opengever.dossier.businesscasedossier', 'dossier1')]
        dossier2 = repo2[repo2.invokeFactory(
            'opengever.dossier.businesscasedossier', 'dossier2')]

        doc1 = createContentInContainer(dossier1,
            'opengever.document.document', title=u'dxc3\xb6c1')

        task1 = dossier1[dossier1.invokeFactory(
            'opengever.task.task', 'task1')]
        subdossier1 = dossier1[dossier1.invokeFactory(
            'opengever.dossier.businesscasedossier', 'subdossier1')]

        # In repo we can't add other content than businescasedossiers
        badrepo1 = portal[portal.invokeFactory(
            'opengever.repository.repositoryfolder', 'badrepo1')]

        # Move-items view
        view = dossier1.restrictedTraverse('move_items')

        # Fallback to document tab when no items are selected
        self.assertTrue("%s#documents" % dossier1.absolute_url() == view())

        # Put original-template to request to test second fallback
        request.form['orig_template'] = "%s#dossiers" % dossier1.absolute_url()
        self.assertTrue("%s#dossiers" % dossier1.absolute_url() == view())

        # Paths of objects to move
        paths = u"%s;;%s;;%s" % \
                 ("/".join(doc1.getPhysicalPath()),
                 "/".join(task1.getPhysicalPath()),
                 "/".join(subdossier1.getPhysicalPath()))

        # Set request vars
        request['paths'] = paths
        request['form.widgets.request_paths'] = paths
        request['form.widgets.destination_folder'] = "/".join(
            badrepo1.getPhysicalPath())

        # Get move_items form
        form = view.form(dossier1, request)
        form.updateWidgets()

        # Set widget values
        form.widgets['destination_folder'].value = badrepo1
        form.widgets['request_paths'].value = paths

        # Check childs bevore moving
        self.assertTrue(dossier1.hasChildNodes() == 3)
        self.assertTrue(dossier2.hasChildNodes() == 0)

        # Move objects
        # We want to put disallowed contenttype into the repo.
        form.handle_submit(form, object)

        # Check childs after moving
        # Its like before because the move-step was invalid
        self.assertTrue(dossier1.hasChildNodes() == 3)
        self.assertTrue(dossier2.hasChildNodes() == 0)

        # Set request vars
        request['paths'] = paths
        request['form.widgets.request_paths'] = paths
        request['form.widgets.destination_folder'] = "/".join(
            dossier2.getPhysicalPath())

        # Get move_items form
        form = view.form(dossier1, request)
        form.updateWidgets()

        # Set widget values
        form.widgets['destination_folder'].value = dossier2
        form.widgets['request_paths'].value = paths

        # Move objects
        # Now we just copy allowed contenttypes
        form.handle_submit(form, object)

        # Check childs after moving
        # And you see... they where moved to the the new dossier
        self.assertTrue(dossier1.hasChildNodes() == 0)
        self.assertTrue(dossier2.hasChildNodes() == 3)

        self.failUnless(portal.unrestrictedTraverse('repo2/dossier2/document-1'))
        self.failUnless(portal.unrestrictedTraverse('repo2/dossier2/task1'))
        self.failUnless(
            portal.unrestrictedTraverse('repo2/dossier2/subdossier1'))

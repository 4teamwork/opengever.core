import unittest2 as unittest
from opengever.dossier.testing import OPENGEVER_DOSSIER_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.testing.z2 import Browser

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

        doc1 = dossier1[dossier1.invokeFactory(
            'opengever.document.document', 'doc1')]
        task1 = dossier1[dossier1.invokeFactory(
            'opengever.task.task', 'task1')]
        subdossier1 = dossier1[dossier1.invokeFactory(
            'opengever.dossier.businesscasedossier', 'subdossier1')]

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
            dossier2.getPhysicalPath())

        # Get move_items form
        form = view.form(dossier1, request)
        form.updateWidgets()

        # Set widget values
        form.widgets['destination_folder'].value = dossier2
        form.widgets['request_paths'].value = paths

        # Check childs bevore moving
        self.assertTrue(dossier1.hasChildNodes() == 3)

        # Move objects
        form.handle_submit(form, object)

        # Check childs after moving
        self.assertTrue(dossier1.hasChildNodes() == 0)

        self.failUnless(portal.unrestrictedTraverse('repo2/dossier2/doc1'))
        self.failUnless(portal.unrestrictedTraverse('repo2/dossier2/task1'))
        self.failUnless(
            portal.unrestrictedTraverse('repo2/dossier2/subdossier1'))

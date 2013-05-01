from ftw.testing import MockTestCase
from mocker import KWARGS
from opengever.repository.repositoryroot import PrimaryRepositoryRoot
from zope.publisher.interfaces import NotFound


class TestPrimaryRepositoryRoot(MockTestCase):

    def setUp(self):
        self.portal_url = self.stub()
        self.mock_tool(self.portal_url, 'portal_url')

        self.site = self.mocker.mock()
        self.expect(self.portal_url.getPortalObject()).result(self.site)


    def test_get_primary_repository_root_raises_404_if_no_root_found(self):
        context = self.stub()
        request = self.stub()

        self.expect(self.site.getFolderContents(KWARGS)).result([])

        self.replay()
        view = PrimaryRepositoryRoot(context, request)

        with self.assertRaises(NotFound):
            view.get_primary_repository_root()

    def test_get_primary_repository_root(self):
        context = self.stub()
        request = self.stub()

        root = self.create_dummy(id='root')
        root1 = self.create_dummy(id='root1')
        root2 = self.create_dummy(id='root2')
        root3 = self.create_dummy(id='root3')
        root17 = self.create_dummy(id='root17')

        query = {'portal_type': ['opengever.repository.repositoryroot']}
        self.expect(self.site.getFolderContents(
                full_objects=True, contentFilter=query)).result([
                root3, root, root17, root2, root1])

        self.replay()
        view = PrimaryRepositoryRoot(context, request)
        self.assertEqual(view.get_primary_repository_root(),
                         root17)

    def test_render_redirects_to_repository_root(self):
        context = self.stub()
        request = self.mocker.mock()

        root1 = self.create_dummy(id='root1')
        root2 = self.mocker.mock()
        self.expect(root2.id).result('root2').count(1, None)
        self.expect(root2.absolute_url()).result('http://nohost/site/root2')

        self.expect(self.site.getFolderContents(KWARGS)).result(
            [root1, root2])

        self.expect(request.RESPONSE.redirect('http://nohost/site/root2'))

        self.replay()
        PrimaryRepositoryRoot(context, request).render()

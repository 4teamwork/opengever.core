from AccessControl import Unauthorized
from mocker import ANY, IN
from opengever.dossier.behaviors.dossier import IDossier, IDossierMarker
from opengever.tasktemplates.browser.form import AddForm
from plone.mocktestcase import MockTestCase
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot


class TestFunctionalForm(MockTestCase):
    """ Functional tests
    """

    def test_load_request_parameters(self):
        """ Test load_request_parameters-method
        """
        # Context
        mock_context = self.mocker.mock()
        self.expect(
            mock_context.absolute_url()).result(
                'http://url.com').count(0, None)

        # Sort_on-Object
        mock_sort_on = self.mocker.mock()
        self.expect(
            mock_sort_on.startswith(ANY)).result(True).count(0, None)
        self.expect(
            mock_sort_on.split(ANY)).result(
                ['header-', 'sortme']).count(0, None)

        # Request
        mock_request = self.mocker.mock()
        self.expect(
            mock_request.get('pagenumber', ANY)).result(3).count(0, None)
        self.expect(
            mock_request.get('sort', ANY)).result(mock_sort_on).count(0, None)
        self.expect(
            mock_request.get('searchable_text')).result(
                'my text to search').count(0, None)
        self.expect(mock_request.get('dir', ANY)).result('ASC').count(0, None)
        self.expect(
            mock_request.__mocker_act__(
                "contains", ('searchable_text', ))).result(True).count(0, None)
        self.expect(
            mock_request.request).result('http://url.com').count(0, None)
        self.expect(
            mock_request.searchable_text).result(
                'http://url.com').count(0, None)

        # AddForm Obj
        mock_addForm = self.mocker.patch(AddForm(mock_context, mock_request))
        self.expect(mock_addForm.pagesize).result(5).count(0, None)
        self.expect(mock_addForm.sort_on).result(mock_sort_on).count(0, None)
        self.expect(mock_addForm.sort_reverse).result('reverse').count(0, None)

        self.replay()

        mock_addForm.load_request_parameters()

        # Check attributes
        self.assertTrue(3 == mock_addForm.batching_current_page)
        self.assertTrue(
            mock_addForm.pagenumber == mock_addForm.batching_current_page)
        self.assertTrue(5 == mock_addForm.batching_pagesize)
        self.assertTrue('http://url.com' == mock_addForm.url)
        self.assertTrue(3 == mock_addForm.batching_current_page)
        self.assertTrue('my text to search' == mock_addForm.filter_text)
        self.assertTrue('asc' == mock_addForm.sort_order)

    def test_javascript_url_debug(self):
        """ Test javascript_url method
        """
        url = self.javascript_url_base()

        # We don't have the right time, so we leave the now param blank.
        expected_url = 'http://url.com/++resource++tasktemplates.form.js?now='

        self.assertTrue(expected_url in url)

    def test_javascript_url_no_debug(self):
        """ Test javascript_url method
        """
        url = self.javascript_url_base(False)

        expected_url = 'http://url.com/++resource++tasktemplates.form.js'

        self.assertTrue(expected_url == url)

    def javascript_url_base(self, debug=True):
        """ Base method to test javascript_url method
        """
        # Context
        mock_context = self.mocker.mock()
        self.expect(
            mock_context.absolute_url()).result(
                'http://url.com').count(0, None)

        # Request
        mock_request = self.mocker.mock()

        # Register Url Tool
        mock_prortal_url = self.mocker.mock()
        self.expect(
            mock_prortal_url()).result('http://url.com')

        self.mock_tool(mock_prortal_url, "portal_url")

        # Register Javascript Tool
        mock_javascript = self.mocker.mock()
        self.expect(
            mock_javascript.getDebugMode()).result(debug)

        self.mock_tool(mock_javascript, "portal_javascripts")

        self.replay()

        mock_addForm = AddForm(mock_context, mock_request)
        return mock_addForm.javascript_url()

    def test_replace_interactive_user_responsible_with_dossier(self):
        """ Test replace_interactive_user method with responsible as principal
        and with a dossier
        """
        # Fake Repository
        mock_siteroot = self.mocker.mock()
        self._obj_provides(mock_siteroot, provided_interfaces=[IPloneSiteRoot])

        mock_repo1 = self.mocker.mock()
        self.expect(mock_repo1.responsible).result('superman')
        self.expect(mock_repo1.__parent__).result(mock_siteroot).count(0, None)

        self._obj_provides(mock_repo1,
                          provided_interfaces=[IDossierMarker, IDossier],
                          not_provided_interfaces=[IPloneSiteRoot])

        # Context
        mock_context = self.mocker.mock()
        self.expect(mock_context.__parent__).result(mock_repo1).count(0, None)

        # Get interactive user
        user = self.replace_interactive_user_base('responsible', mock_context)

        # Check
        self.assertTrue('superman' == user)

    def test_replace_interactive_user_responsible_no_dossier(self):
        """ Test replace_interactive_user method with responsible as principal
        and without a dossier
        """
        # Fake Repository
        mock_siteroot = self.mocker.mock()
        self._obj_provides(mock_siteroot,
            provided_interfaces=[IPloneSiteRoot],
            not_provided_interfaces=[IDossierMarker])

        # Context
        mock_context = self.mocker.mock()
        self.expect(
            mock_context.__parent__).result(mock_siteroot).count(0, None)

        self.assertRaises(
            ValueError,
            self.replace_interactive_user_base,
            'responsible',
            mock_context)

    def test_replace_interactive_user_current_user(self):
        """ Test replace_interactive_user method with current_user as principal
        """
        # Context
        mock_context = self.mocker.mock()

        # Member
        mock_member = self.mocker.mock()
        self.expect(mock_member.getId()).result('superman')

        # Register Membership Tool
        mock_mtool = self.mocker.mock()
        self.expect(
            mock_mtool.getAuthenticatedMember()).result(mock_member)

        self.mock_tool(mock_mtool, 'portal_membership')

        user = self.replace_interactive_user_base('current_user', mock_context)

        self.assertTrue('superman' == user)

    def test_replace_interactive_user_no_members(self):
        """ Test replace_interactive_user method with no members found
        """
        # Context
        mock_context = self.mocker.mock()

        # Register Membership Tool
        mock_mtool = self.mocker.mock()
        self.expect(
            mock_mtool.getAuthenticatedMember()).result('')

        self.mock_tool(mock_mtool, 'portal_membership')

        self.assertRaises(
            Unauthorized,
            self.replace_interactive_user_base,
            'current_user',
            mock_context)

    def test_replace_interactive_user_not_handled(self):
        """ Test replace_interactive_user method with no principal handled
        """
        # Context
        mock_context = self.mocker.mock()

        user = self.replace_interactive_user_base('slevin', mock_context)
        self.assertTrue('slevin' == user)

    def replace_interactive_user_base(self, principal, context):
        """ Base method to test replace_interactive_user method
        """

        mock_context = context

        # Request
        mock_request = self.mocker.mock()

        self.replay()

        mock_addForm = AddForm(mock_context, mock_request)

        return mock_addForm.replace_interactive_user(principal)

    def _obj_provides(
        self, obj, provided_interfaces=[], not_provided_interfaces=[]):
        """ That we can use Interface.providedBy(obj) we need this method.

        For all interfaces in provided_interfaces it return True,
        for all interfaces in not_provided_interfaces it return False
        """
        assert hasattr(provided_interfaces, '__iter__')
        assert hasattr(not_provided_interfaces, '__iter__')
        self.expect(obj.__providedBy__.extends).result(1).count(0, None)
        self.expect(obj.__providedBy__(
            IN(provided_interfaces))).result(True).count(0, None)
        self.expect(obj.__providedBy__(
            IN(not_provided_interfaces))).result(False).count(0, None)

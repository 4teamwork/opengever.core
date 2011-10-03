from mocker import ANY
from opengever.tasktemplates.browser.form import AddForm
from plone.mocktestcase import MockTestCase


class TestFunctionalHelper(MockTestCase):
    """ Functional tests
    """

    def test_load_request_parameters(self):
        """ Test interactive_user_helper-method
        """
        # Context
        mock_context = self.mocker.mock()
        self.expect(mock_context.absolute_url()).result('http://url.com').count(0, None)

        # Sort_on-Object
        mock_sort_on = self.mocker.mock()
        self.expect(mock_sort_on.startswith(ANY)).result(True).count(0, None)
        self.expect(mock_sort_on.split(ANY)).result(['header-', 'sortme']).count(0, None)

        # Request
        mock_request = self.mocker.mock()
        self.expect(mock_request.get('pagenumber', ANY)).result(3).count(0, None)
        self.expect(mock_request.get('sort', ANY)).result(mock_sort_on).count(0, None)
        self.expect(mock_request.get('searchable_text')).result('my text to search').count(0, None)
        self.expect(mock_request.get('dir', ANY)).result('ASC').count(0, None)
        self.expect(mock_request.__mocker_act__("contains", ('searchable_text',))).result(True).count(0, None)
        self.expect(mock_request.request).result('http://url.com').count(0, None)
        self.expect(mock_request.searchable_text).result('http://url.com').count(0, None)

        # AddForm Obj
        mock_addForm = self.mocker.patch(AddForm(mock_context, mock_request))
        self.expect(mock_addForm.pagesize).result(5).count(0, None)
        self.expect(mock_addForm.sort_on).result(mock_sort_on).count(0, None)
        self.expect(mock_addForm.sort_reverse).result('reverse').count(0, None)

        self.replay()

        mock_addForm.load_request_parameters()

        # Check attributes
        self.assertTrue(3 == mock_addForm.batching_current_page)
        self.assertTrue(mock_addForm.pagenumber == mock_addForm.batching_current_page)
        self.assertTrue(5 == mock_addForm.batching_pagesize)
        self.assertTrue('http://url.com' == mock_addForm.url)
        self.assertTrue(3 == mock_addForm.batching_current_page)
        self.assertTrue('my text to search' == mock_addForm.filter_text)
        self.assertTrue('asc' == mock_addForm.sort_order)


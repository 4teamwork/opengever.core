from Products.CMFPlone.interfaces import IPloneSiteRoot
from ftw.testing import MockTestCase
from mocker import ANY
from opengever.inbox.browser.transitioncontroller import ForwardingTransitionController
from opengever.ogds.base.interfaces import IContactInformation
from zope.app.component.hooks import setSite
from zope.component import getSiteManager
from zope.interface import alsoProvides


class TestTaskTransitionController(MockTestCase):

    def setUp(self):
        # we need to have a site root for making the get_client_id cachecky
        # work.
        root = self.create_dummy(getSiteManager=getSiteManager, id='root')
        alsoProvides(root, IPloneSiteRoot)
        setSite(root)

    def test_is_succesor_forwarding_proccses(self):
        f1= self.mocker.mock()
        mock_request = self.mocker.mock()

        with self.mocker.order():
            self.expect(mock_request.get('X-CREATING-SUCCESSOR')).result(None)
            self.expect(mock_request.get('X-CREATING-SUCCESSOR')).result(False)
            self.expect(mock_request.get('X-CREATING-SUCCESSOR')).result(True)

        self.replay()
        self.assertFalse(
            ForwardingTransitionController(f1, mock_request)._is_succesor_forwarding_proccses())
        self.assertFalse(
            ForwardingTransitionController(f1, mock_request)._is_succesor_forwarding_proccses())
        self.assertTrue(ForwardingTransitionController(f1, mock_request)._is_succesor_forwarding_proccses())

    def test_is_current_inbox_group_user(self):
        f1 = self.stub()
        mock_request = self.mocker.mock()
        contact_info = self.mocker.mock()
        self.mock_utility(contact_info, IContactInformation, name=u"")

        with self.mocker.order():
            self.expect(contact_info.is_user_in_inbox_group()).result(False)
            self.expect(contact_info.is_user_in_inbox_group()).result(True)

        self.replay()
        self.assertFalse(
            ForwardingTransitionController(f1, mock_request)._is_current_inbox_group_user())
        self.assertTrue(
            ForwardingTransitionController(f1, mock_request)._is_current_inbox_group_user())

    def test_is_assign_to_dossier_or_reassing_possible(self):
        controller, controller_mock, f1 = self._create_forwarding_controller()
        with self.mocker.order():
            self.expect(controller_mock._is_current_inbox_group_user()).result(False)
            self.expect(controller_mock._is_current_inbox_group_user()).result(True)

            self.expect(controller_mock._is_current_inbox_group_user()).result(False)
            self.expect(controller_mock._is_current_inbox_group_user()).result(True)

            self.expect(controller_mock._is_current_inbox_group_user()).result(False)
            self.expect(controller_mock._is_current_inbox_group_user()).result(True)

        self.replay()
        transitions = [
            'forwarding-transition-assign-to-dossier',
            'forwarding-transition-reassign',
            'forwarding-transition-close']

        for transition in transitions:
            self.assertFalse(controller.is_transition_possible(transition))
            self.assertTrue(controller.is_transition_possible(transition))

    def test_is_accept_possible(self):
        controller, controller_mock, f1 = self._create_forwarding_controller()
        with self.mocker.order():
            self.expect(controller_mock._is_multiclient_setup()).result(False)

            self.expect(controller_mock._is_multiclient_setup()).result(True)
            self.expect(controller_mock._is_task_on_responsible_client()).result(False)
            self.expect(controller_mock._is_succesor_forwarding_proccses()).result(False)

            self.expect(controller_mock._is_multiclient_setup()).result(True)
            self.expect(controller_mock._is_task_on_responsible_client()).result(False)
            self.expect(controller_mock._is_succesor_forwarding_proccses()).result(True)
            self.expect(controller_mock._is_inbox_group_user()).result(False)

            self.expect(controller_mock._is_multiclient_setup()).result(True)
            self.expect(controller_mock._is_task_on_responsible_client()).result(True)
            self.expect(controller_mock._is_inbox_group_user()).result(False)

            self.expect(controller_mock._is_multiclient_setup()).result(True)
            self.expect(controller_mock._is_task_on_responsible_client()).result(True)
            self.expect(controller_mock._is_inbox_group_user()).result(True)

        self.replay()
        transition = 'forwarding-transition-accept'

        self.assertFalse(controller.is_transition_possible(transition))
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertFalse(controller.is_transition_possible(transition))
        self.assertTrue(controller.is_transition_possible(transition))


    def _create_forwarding_controller(self):
        f1 = self.stub()
        self.expect(f1.absolute_url()).result(
            'http://nohost/plone/f1').count(0, None)
        self.expect(f1.getPhysicalPath()).result(
            ['', 'plone', 'f1']).count(0, None)

        controller = ForwardingTransitionController(f1, {})
        controller_mock = self.mocker.patch(controller)

        return controller, controller_mock, f1

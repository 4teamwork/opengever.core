from ftw.builder import Builder
from ftw.builder import create
from opengever.task.browser.accept.utils import accept_forwarding_with_successor
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestForwardingAccepting(FunctionalTestCase):

    def test_successor_task_is_created_with_information_task_type(self):
        inbox = create(Builder('inbox'))
        dossier = create(Builder('dossier'))
        forwarding = create(Builder('forwarding')
                            .having(responsible=TEST_USER_ID,
                                    responsible_client='org-unit-1',
                                    issuer='hugo.boss')
                            .within(inbox))
        task = accept_forwarding_with_successor(
            self.portal, forwarding.oguid.id, 'OK, thx.', dossier=dossier)

        self.assertEquals('information', task.task_type)

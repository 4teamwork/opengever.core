from opengever.testing import IntegrationTestCase
from opengever.base.transition import TransitionExtender
from opengever.base.transition import ITransitionExtender


class TestTransitionExtender(IntegrationTestCase):

    def test_implements_interface(self):
        verifyClass(ITransitionExtender, TransitionExtender)

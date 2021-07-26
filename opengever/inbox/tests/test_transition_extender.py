from ftw.builder import Builder
from ftw.builder import create
from opengever.base.transition import ITransitionExtender
from opengever.testing import FunctionalTestCase
from plone import api
from zope.component import queryMultiAdapter


class TestForwardingTransitionExtendersRegistered(FunctionalTestCase):

    OK_TRANSITIONS_WITHOUT_EXTENDER = []

    def test_forwarding_transition_extenders_registered(self):
        forwarding = create(Builder("forwarding"))

        wftool = api.portal.get_tool("portal_workflow")
        chain = wftool.getChainForPortalType("opengever.inbox.forwarding")[0]
        workflow = wftool.get(chain)

        for transition_name in list(workflow.transitions):
            extender = queryMultiAdapter(
                (forwarding, self.request),
                ITransitionExtender,
                transition_name,
            )
            if (
                not extender
                and transition_name not in self.OK_TRANSITIONS_WITHOUT_EXTENDER
            ):
                self.fail(
                    "Could not find a transition extender for forwarding "
                    "workflow transition '{}'. Either register an "
                    "'ITransitionExtender' or add the transition to the "
                    "whitelist.".format(transition_name)
                )

from ftw.builder import Builder
from ftw.builder import create
from opengever.base.transition import ITransitionExtender
from opengever.testing import FunctionalTestCase
from plone import api
from zope.component import queryMultiAdapter


class TestTaskTransitionExtendersRegistered(FunctionalTestCase):

    OK_TRANSITIONS_WITHOUT_EXTENDER = [
        # this transition is executed automatically when creating tasks from
        # a task template. No user input can be made at any point an thus we
        # dont need a transition extender
        "task-transition-open-planned",
    ]

    def test_task_transition_extenders_registered(self):
        task = create(Builder("task"))

        wftool = api.portal.get_tool("portal_workflow")
        chain = wftool.getChainForPortalType("opengever.task.task")[0]
        workflow = wftool.get(chain)

        for transition_name in list(workflow.transitions):
            extender = queryMultiAdapter(
                (task, self.request),
                ITransitionExtender,
                transition_name,
            )
            if (
                not extender
                and transition_name not in self.OK_TRANSITIONS_WITHOUT_EXTENDER
            ):
                self.fail(
                    "Could not find a transition extender for task "
                    "workflow transition '{}'. Either register an "
                    "'ITransitionExtender' or add the transition to the "
                    "whitelist.".format(transition_name)
                )

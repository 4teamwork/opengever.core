from contextlib import contextmanager
from ftw.upgrade import UpgradeStep
from ftw.upgrade.workflow import WorkflowChainUpdater


class EnableCommitteeLawgiverWorkflows(UpgradeStep):
    """Enable committee lawgiver workflows.
    """

    def __call__(self):
        with self.activate_lawgiver_workflow(
                'opengever.meeting.committeecontainer', {
                    ('opengever_committeecontainer_workflow',
                     'opengever_committeecontainer_workflow'): {
                         'committeecontainer-state-active':
                         'opengever_committeecontainer_workflow--STATUS--active'}}):
            with self.activate_lawgiver_workflow(
                    'opengever.meeting.committee', {
                        ('opengever_committee_workflow',
                         'opengever_committee_workflow'): {
                             'committee-state-active':
                             'opengever_committee_workflow--STATUS--active'}}):
                self.install_upgrade_profile()

    @contextmanager
    def activate_lawgiver_workflow(self, portal_type, review_state_mapping):
        objects = self.catalog_unrestricted_search({'portal_type': portal_type},
                                                   full_objects=True)

        with WorkflowChainUpdater(objects, review_state_mapping):
            yield

        # Remove all old states from all old workflows so that we have a
        # clean new state.
        portal_workflow = self.getToolByName('portal_workflow')
        for ((old_wf, new_wf), state_mapping) in review_state_mapping.items():
            states = portal_workflow.get(old_wf).states
            states.deleteStates(
                [old_state for old_state in state_mapping.keys()
                 if old_state in states])

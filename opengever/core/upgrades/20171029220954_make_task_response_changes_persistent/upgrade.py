from ftw.upgrade import UpgradeStep
from opengever.task.adapters import IResponseContainer
from opengever.task.task import ITask
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping


class MakeTaskResponseChangesPersistent(UpgradeStep):
    """Make task response changes persistent.
    """

    # This upgrade step was retroactively marked as deferrable.
    # No need to run this upgradestep immediately.
    deferrable = True

    def __call__(self):
        for task in self.objects({'object_provides': ITask.__identifier__},
                                'Make task responses persistent'):
            self.make_responses_persistent(task)

    def make_responses_persistent(self, task):
        responses = IResponseContainer(task)
        for response in responses:
            if response.changes:
                changes = [
                    PersistentMapping(change) for change in response.changes]
                response.changes = PersistentList(changes)

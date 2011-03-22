from Products.Five import BrowserView
from zope.interface import Interface


class ITaskWorkflowChecks(Interface):
    """The TaskWorkflowChecks view provides various functions for
    checking whether certain worfklow transitions are allowed to
    execute or not.
    """

    def is_unidirectional():
        """Returns `True` if the task_type is of kind "unidirectional".
        """

    def is_bidirectional():
        """Returns `True` if the task_type is of kind "bidirectional".
        """


class TaskWorfklowChecks(BrowserView):
    """see ITaskWorkflowChecks
    """

    def is_unidirectional(self):
        """see ITaskWorkflowChecks
        """
        categories = ['unidirectional_by_reference',
                      'unidirectional_by_value']
        return self.context.task_type_category in categories

    def is_bidirectional(self):
        """see ITaskWorkflowChecks
        """
        categories = ['bidirectional_by_reference',
                      'bidirectional_by_value']
        return self.context.task_type_category in categories

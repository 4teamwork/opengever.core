from zope.i18nmessageid import MessageFactory

_ = MessageFactory("opengever.task")


OPEN_TASK_STATES = [
        'task-state-open',
        'task-state-in-progress',
        'task-state-resolved',
        'task-state-rejected',
        'forwarding-state-open',
        'forwarding-state-refused',
    ]

CLOSED_TASK_STATES = [
        'task-state-cancelled',
        'task-state-tested-and-closed',
    ]

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

FINISHED_TASK_STATES = [
    'task-state-tested-and-closed',
    'task-state-rejected',
    'task-state-cancelled'
]

TASK_STATE_PLANNED = 'task-state-planned'

FINAL_TASK_STATES = [
    'task-state-tested-and-closed',
    'task-state-cancelled',
    'task-state-skipped'
]

FINAL_TRANSITIONS = [
    'task-transition-open-cancelled',
    'task-transition-open-tested-and-closed',
    'task-transition-in-progress-tested-and-closed',
    'task-transition-resolved-tested-and-closed',
    'task-transition-planned-skipped']

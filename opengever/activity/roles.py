from zope.i18nmessageid import MessageFactory

_ = MessageFactory("opengever.activity")


TASK_ISSUER_ROLE = 'task_issuer'
TASK_RESPONSIBLE_ROLE = 'task_responsible'
TASK_OLD_RESPONSIBLE_ROLE = 'task_old_responsible'
DISPOSITION_RECORDS_MANAGER_ROLE = 'records_manager'
DISPOSITION_ARCHIVIST_ROLE = 'archivist'
WATCHER_ROLE = 'regular_watcher'
COMMITTEE_RESPONSIBLE_ROLE = 'committee_responsible'
PROPOSAL_ISSUER_ROLE = 'proposal_issuer'
TASK_REMINDER_WATCHER_ROLE = 'task_reminder_watcher_role'
DOSSIER_RESPONSIBLE_ROLE = 'dossier_responsible_role'
TODO_RESPONSIBLE_ROLE = 'todo_responsible_role'
WORKSPACE_MEMBER_ROLE = 'workspace_member_role'

_('task_issuer', default=u"Task issuer")
_('task_responsible', default=u"Task responsible")
_('task_old_responsible', default=u"Task former responsible")
_('records_manager', default=u"Records Manager")
_('archivist', default=u"Archivist")
_('regular_watcher', default=u"Watcher")
_('proposal_issuer', default=u"Proposal issuer")
_('committee_responsible', default=u"Committee responsible")
_('task_reminder_watcher_role', default=u"Watcher")
_('dossier_responsible_role', default=u"Dossier responsible")
_('todo_responsible_role', default=u"ToDo responsible")
_('workspace_member_role', default=u"Workspace member")

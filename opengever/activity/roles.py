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

ROLE_TRANSLATIONS = {
    TASK_ISSUER_ROLE: _('task_issuer', default=u"Task issuer"),
    TASK_RESPONSIBLE_ROLE: _('task_responsible', default=u"Task responsible"),
    TASK_OLD_RESPONSIBLE_ROLE: _('task_old_responsible', default=u"Task former responsible"),
    DISPOSITION_RECORDS_MANAGER_ROLE: _('records_manager', default=u"Records Manager"),
    DISPOSITION_ARCHIVIST_ROLE: _('archivist', default=u"Archivist"),
    WATCHER_ROLE: _('regular_watcher', default=u"Watcher"),
    PROPOSAL_ISSUER_ROLE: _('proposal_issuer', default=u"Proposal issuer"),
    COMMITTEE_RESPONSIBLE_ROLE: _('committee_responsible', default=u"Committee responsible"),
    TASK_REMINDER_WATCHER_ROLE: _('task_reminder_watcher_role', default=u"Watcher"),
    DOSSIER_RESPONSIBLE_ROLE: _('dossier_responsible_role', default=u"Dossier responsible"),
    TODO_RESPONSIBLE_ROLE: _('todo_responsible_role', default=u"ToDo responsible"),
    WORKSPACE_MEMBER_ROLE: _('workspace_member_role', default=u"Workspace member")
}

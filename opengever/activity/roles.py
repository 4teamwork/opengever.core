from zope.i18nmessageid import MessageFactory

_ = MessageFactory("opengever.activity")


TASK_ISSUER_ROLE = 'task_issuer'
TASK_RESPONSIBLE_ROLE = 'task_responsible'
TASK_OLD_RESPONSIBLE_ROLE = 'task_old_responsible'
DISPOSITION_RECORDS_MANAGER_ROLE = 'records_manager'
DISPOSITION_ARCHIVIST_ROLE = 'archivist'
WATCHER_ROLE = 'regular_watcher'


_('task_issuer', default=u"Task issuer")
_('task_responsible', default=u"Task responsible")
_('task_old_responsible', default=u"Task former responsible")
_('records_manager', default=u"Records Manager")
_('archivist', default=u"Archivist")
_('regular_watcher', default=u"Watcher")

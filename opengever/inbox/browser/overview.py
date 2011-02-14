from five import grok
from opengever.dossier.browser.overview import DossierOverview
from opengever.globalindex.interfaces import ITaskQuery
from opengever.globalindex.model.task import Task
from opengever.inbox.inbox import IInbox
from opengever.ogds.base.utils import get_client_id
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory


class InboxOverview(DossierOverview):
    grok.context(IInbox)
    grok.name('tabbedview_view-overview')

    def boxes(self):

        #TODO: implements the sharing box n ot work yet
        # dict(id = 'sharing', content=self.sharing())],
        items = [[dict(id='assigned_tasks',
                       content=self.inbox_forwardings(),
                       label=MessageFactory('ftw.tabbedview')(u'assigned_tasks')),],

                 [dict(id='documents',
                       content=self.documents()), ]]
        return items

    def inbox_forwardings(self):

        principal = 'inbox:%s' % get_client_id()

        query_util = getUtility(ITaskQuery)

        query = query_util._get_tasks_for_responsible_query(
            principal, 'modified')
        query = query.filter(Task.review_state=='task-state-open').filter(
        Task.client_id != get_client_id())
        for item in query.all():
            item.icon = item.icon.replace(item.client_id+'/', '')
        return query.all()

from Products.CMFCore.utils import getToolByName
from five import grok
from opengever.base.browser.helper import get_css_class
from opengever.dossier.browser.overview import DossierOverview
from opengever.globalindex.interfaces import ITaskQuery
from opengever.globalindex.model.task import Task
from opengever.inbox import _
from opengever.inbox.browser.tabs import get_current_inbox_principal
from opengever.inbox.inbox import IInbox
from opengever.ogds.base.utils import get_client_id
from opengever.task import OPEN_TASK_STATES
from sqlalchemy import and_, or_
from zope.component import getUtility


class InboxOverview(DossierOverview):
    """Displayes the Inbox Overview
    """
    grok.context(IInbox)
    grok.name('tabbedview_view-overview')

    def boxes(self):
        """Defines the boxes wich are Displayed at the Overview tab"""

        items = [[dict(id='assigned_inbox_tasks',
                       content=self.assigned_tasks(),
                       label=_(u'label_assigned_inbox_tasks',
                               default='Assigned tasks')),
                  dict(id='issued_inbox_tasks',
                       content=self.issued_tasks(),
                       label=_(u'label_issued_inbox_tasks',
                               default='Issued tasks')), ],
                 [dict(id='documents',
                       content=self.documents()), ]]
        return items

    def assigned_tasks(self):
        """
        Get tasks that have been created on a different client and
        are assigned to this client's inbox.
        """
        query_util = getUtility(ITaskQuery)
        query = query_util._get_tasks_for_responsible_query(
            get_current_inbox_principal(self.context))

        query = query.filter(Task.review_state.in_(OPEN_TASK_STATES))

        # If a task has a successor task, it should only list one of them,
        # the one which is physically one the current client.
        query = query.filter(
            or_(
                and_(Task.predecessor == None, Task.successors == None),
                Task.client_id == get_client_id()))

        return query.all()[:5]

    def issued_tasks(self):
        types = ['opengever.task.task', 'opengever.inbox.forwarding']
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog(portal_type=types,
                          issuer=get_current_inbox_principal(self.context),
                          review_state=OPEN_TASK_STATES)

        return results[:5]

    def documents(self):
        """
        Get documents and mails that are directly contained in
        the inbox, but not in forwardings.
        """
        catalog = self.context.portal_catalog
        query = {'isWorkingCopy': 0,
                 'path': {'depth': 1,
                          'query': '/'.join(self.context.getPhysicalPath())},
                 'portal_type': ['opengever.document.document',
                                 'ftw.mail.mail']}
        documents = catalog(query)[:10]

        document_list = [{
            'Title': document.Title,
            'getURL': document.getURL,
            'alt': document.document_date and
                document.document_date.strftime('%d.%m.%Y') or '',
            'css_class': get_css_class(document),
            'portal_type': document.portal_type,
        } for document in documents]

        return document_list

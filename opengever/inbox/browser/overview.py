from opengever.base.browser.boxes_view import BoxesViewMixin
from opengever.base.browser.helper import get_css_class
from opengever.globalindex.model.task import Task
from opengever.inbox import _
from opengever.ogds.base.utils import get_current_org_unit
from opengever.tabbedview import GeverTabMixin
from opengever.task import OPEN_TASK_STATES
from plone import api
from plone.app.contentlisting.interfaces import IContentListing
from Products.Five.browser import BrowserView
from sqlalchemy import desc


class InboxOverview(BoxesViewMixin, BrowserView, GeverTabMixin):

    show_searchform = False

    def boxes(self):
        """Defines the boxes wich are Displayed at the Overview tab"""

        return [
            [
                dict(id='assigned_inbox_tasks',
                     content=self.assigned_tasks(),
                     href='assigned_inbox_tasks',
                     label=_(u'label_assigned_inbox_tasks',
                             default='Assigned tasks')),
                dict(id='issued_inbox_tasks',
                     href='issued_inbox_tasks',
                     content=self.issued_tasks(),
                     label=_(u'label_issued_inbox_tasks',
                             default='Issued tasks')),
            ], [
                dict(id='documents',
                     href='documents',
                     label=_("Documents"),
                     content=self.documents()),
            ]
        ]

    def assigned_tasks(self):
        """Returns the 5 last modified open task which are assigned
        to the current org unit's inbox.
        """
        current_inbox_id = get_current_org_unit().inbox().id()
        query = Task.query.users_tasks(current_inbox_id)
        query = query.filter(Task.review_state.in_(OPEN_TASK_STATES))
        query = query.order_by(desc(Task.modified))

        return query.limit(5).all()

    def issued_tasks(self):
        """Returns the 5 last modified open task which are issued
        by the current org unit's inbox.
        """
        current_inbox_id = get_current_org_unit().inbox().id()
        query = Task.query.users_issued_tasks(current_inbox_id)
        query = query.filter(Task.review_state.in_(OPEN_TASK_STATES))
        query = query.order_by(desc(Task.modified))

        return query.limit(5).all()

    def documents(self):
        """
        Get documents and mails that are directly contained in
        the inbox, but not in forwardings.
        """

        catalog = api.portal.get_tool(name='portal_catalog')

        query = {'isWorkingCopy': 0,
                 'path': {'depth': 1,
                          'query': '/'.join(self.context.getPhysicalPath())},
                 'object_provides': [
                     'opengever.document.behaviors.IBaseDocument', ],
                 'sort_on': 'modified',
                 'sort_order': 'reverse'}

        documents = catalog(query)[:10]
        document_list = IContentListing(documents)
        return document_list

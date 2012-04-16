from five import grok
from opengever.base.browser.helper import get_css_class
from opengever.dossier.browser.overview import DossierOverview
from opengever.globalindex.interfaces import ITaskQuery
from opengever.globalindex.model.task import Task
from opengever.inbox.inbox import IInbox
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.utils import get_client_id
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory


class InboxOverview(DossierOverview):
    """Displayes the Inbox Overview
    """
    grok.context(IInbox)
    grok.name('tabbedview_view-overview')

    def boxes(self):
        """Defines the boxes wich are Displayed at the Overview tab"""
        #TODO: implement the sharing box - doesn't work yet
        # dict(id = 'sharing', content=self.sharing())],
        items = [[dict(id='inbox', # Eingang
                       content=self.inbox(),
                       label=MessageFactory('ftw.tabbedview')\
                       (u'assigned_forwardings')),

                  dict(id='assigned_tasks', # Aufgaben aus anderem Mandant
                       content=self.assigned_tasks(),
                       label=MessageFactory('ftw.tabbedview')\
                       (u'assigned_tasks')),
                 ],

                 [dict(id='documents', # Dokumente
                       content=self.documents()), ]
                ]
        return items

    def assigned_tasks(self):
        """
        Get tasks that have been created on a different client and
        are assigned to this client's inbox.
        """
        query_util = getUtility(ITaskQuery)

        principal = 'inbox:%s' % get_client_id()
        query = query_util._get_tasks_for_responsible_query(\
                principal, 'modified')
        query = query.filter(Task.review_state=='task-state-open')
        query = query.filter(Task.client_id != get_client_id())

        return query.all()

    def documents(self):
        """
        Get documents and mails that are directly contained in
        the inbox, but not in forwardings.
        """
        catalog = self.context.portal_catalog
        query = {'isWorkingCopy': 0,
                 'path': {'depth': 1,
                          'query': "/%s/eingangskorb" % get_client_id()},
                 'portal_type': ['opengever.document.document',
                                 'ftw.mail.mail']}
        documents = catalog(query)[:10]

        document_list = [{
            'Title': document.Title,
            'getURL': document.getURL,
            'alt': document.document_date and \
                document.document_date.strftime('%d.%m.%Y') or '',
            'css_class': get_css_class(document),
            'portal_type': document.portal_type,
        } for document in documents]

        return document_list


    def inbox(self):
        """
        Get forwardings assigned to this client's inbox.
        """
        principal = 'inbox:%s' % get_client_id()

        # Get the current client's ID
        registry = getUtility(IRegistry)
        client_config = registry.forInterface(IClientConfiguration)
        current_client_id = client_config.client_id

        query_util = getUtility(ITaskQuery)
        query = query_util._get_tasks_for_responsible_query(principal).filter(
                        Task.review_state == 'forwarding-state-open').filter(
                            Task.client_id != current_client_id)
        return query.all()

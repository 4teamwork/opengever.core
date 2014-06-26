from five import grok
from opengever.task.response_description import ResponseDescription
from opengever.task.task import ITask
from opengever.task.viewlets.response import BeneathTask
from plone import api


class ActionMenuViewlet(grok.Viewlet):
    """Display the message subject
    """
    grok.name('opengever.task.ActionMenuViewlet')
    grok.context(ITask)
    grok.require('zope2.View')
    grok.viewletmanager(BeneathTask)
    grok.order(1)

    def get_menu_items(self):
        wftool = api.portal.get_tool(name='portal_workflow')
        infos = wftool.listActionInfos(object=self.context)

        for info in infos:
            description = ResponseDescription.get(transition=info['id'])
            info['response_description'] = description

        return infos

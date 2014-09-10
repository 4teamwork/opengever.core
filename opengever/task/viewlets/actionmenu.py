from five import grok
from opengever.task.response_description import ResponseDescription
from opengever.task.task import ITask
from opengever.task.viewlets.manager import BeneathTask
from plone import api
from zope.component import getMultiAdapter


class ActionMenuViewlet(grok.Viewlet):
    """Display the message subject
    """
    grok.name('opengever.task.ActionMenuViewlet')
    grok.context(ITask)
    grok.require('zope2.View')
    grok.viewletmanager(BeneathTask)
    grok.order(1)

    regular_items = None
    agency_items = None

    def get_menu_items(self):
        regular_items = []
        agency_items = []

        wftool = api.portal.get_tool(name='portal_workflow')
        infos = wftool.listActionInfos(object=self.context, check_condition=False)

        controller = getMultiAdapter((self.context, self.request),
                                     name='task_transition_controller')
        for info in infos:
            description = ResponseDescription.get(transition=info['id'])
            info['response_description'] = description

            if controller.is_transition_possible(info.get('id'), include_agency=False):
                regular_items.append(info)
            else:
                agency_items.append(info)

        self.regular_items = regular_items
        self.agency_items = agency_items

        return regular_items, agency_items

    def get_regular_items(self):
        if self.regular_items is None:
            self.get_menu_items()

        return self.regular_items

    def get_agency_items(self):
        if self.agency_items is None:
            self.get_menu_items()

        return self.agency_items

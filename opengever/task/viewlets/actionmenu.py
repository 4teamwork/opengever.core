from opengever.task.interfaces import ICommentResponseHandler
from opengever.task.response_description import ResponseDescription
from opengever.webactions.interfaces import IWebActionsRenderer
from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter


class ActionMenuViewlet(ViewletBase):
    """Display the message subject
    """

    regular_items = None
    agency_items = None
    webactions_items = None

    def available(self):
        return True

    def get_menu_items(self):
        regular_items = []
        agency_items = []

        self._append_workflow_menu_items(regular_items, agency_items)
        self._append_additional_menu_items(regular_items, agency_items)

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

    def get_webaction_items(self):
        renderer = getMultiAdapter((self.context, self.request),
                                   IWebActionsRenderer, name='action-buttons')
        return renderer()

    def _append_workflow_menu_items(self, regular_items, agency_items):
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

    def _append_additional_menu_items(self, regular_items, agency_items):
        if ICommentResponseHandler(self.context).is_allowed():
            regular_items.append(
                {'title': 'label_add_comment',
                 'url': '{}/@@addcommentresponse'.format(self.context.absolute_url()),
                 'response_description': ResponseDescription.get(transition='task-commented')})

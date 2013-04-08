from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from five import grok
from opengever.task.interfaces import IYearfolderStorer
from opengever.task.task import ITask
from opengever.task.util import change_task_workflow_state
from zExceptions import Unauthorized


class StoreForwardingInYearfolderView(grok.View):
    grok.name('store_forwarding_in_yearfolder')
    grok.context(ITask)
    grok.require('zope2.View')

    def render(self):
        if self.is_already_done():
            # Set correct content type for text response
            self.request.response.setHeader("Content-type", "tex/plain")

            return 'OK'

        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()

        if not member.checkPermission('Add portal content', self.context):
            raise Unauthorized()

        successor_oguid = self.request.get('successor_oguid')
        transition = self.request.get('transition')
        response_text = self.request.get('response_text')

        if transition:
            change_task_workflow_state(self.context,
                                      transition,
                                      text=response_text,
                                      successor_oguid=successor_oguid)

        IYearfolderStorer(self.context).store_in_yearfolder()

        # Set correct content type for text response
        self.request.response.setHeader("Content-type", "tex/plain")

        return 'OK'

    def is_already_done(self):
        """When the sender (caller of this view) has a conflict error, this
        view is called on the receiver multiple times, even when the changes
        are already done the first time. We need to detect such requests and
        tell the sender that it has worked.
        """

        parent = aq_parent(aq_inner(self.context))
        if parent.portal_type == 'opengever.inbox.yearfolder':
            return True
        else:
            return False

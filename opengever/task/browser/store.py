from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.request import tracebackify
from opengever.base.utils import ok_response
from opengever.task.interfaces import IYearfolderStorer
from opengever.task.util import change_task_workflow_state
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from zExceptions import Unauthorized


@tracebackify
class StoreForwardingInYearfolderView(BrowserView):

    def __call__(self):
        if self.is_already_done():
            return ok_response()

        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()

        if not member.checkPermission('Add portal content', self.context):
            raise Unauthorized()

        successor_oguid = self.request.get('successor_oguid')
        transition = self.request.get('transition')
        response_text = safe_unicode(self.request.get('response_text'))

        if transition:
            change_task_workflow_state(self.context,
                                       transition,
                                       text=response_text,
                                       successor_oguid=successor_oguid)

        IYearfolderStorer(self.context).store_in_yearfolder()

        return ok_response()

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

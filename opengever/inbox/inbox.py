from five import grok
from opengever.inbox import _
from plone.directives import form
from opengever.tabbedview.browser.tabs import Tasks
from opengever.task.browser.globaltasks import TaskBaseListing
from opengever.ogds.base.utils import get_client_id
from opengever.globalindex.interfaces import ITaskQuery
from zope import schema
from zope.component import getUtility


class IInbox(form.Schema):
    """ Inbox for OpenGever
    """

    form.fieldset(
        u'common',
        label = _(u'fieldset_common', default=u'Common'),
        fields = [
            u'inbox_group',
            ],
        )

    inbox_group = schema.TextLine(
         title = _(u'label_inbox_group', default=u'Inbox Group'),
         description = _(u'help_inbox_group', default=u''),
         required = False,
         )


class GivenTasks(Tasks):
    grok.name('tabbedview_view-given_tasks')


class AssignedTasks(TaskBaseListing):

    def search(self):
        query_util = getUtility(ITaskQuery)
        self.contents = query_util.get_tasks_for_responsible(
            'inbox:%s' % get_client_id(), self.sort_on, self.sort_order)
        self.len_results = len(self.contents)

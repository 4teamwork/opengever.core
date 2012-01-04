from Products.CMFCore.utils import getToolByName
from opengever.task import _
from opengever.task.util import add_simple_response


def accept_task_with_response(task, response_text, successor_oguid=None):
    response = add_simple_response(task, text=response_text,
                                   successor_oguid=successor_oguid)

    transition = 'task-transition-open-in-progress'
    wftool = getToolByName(task, 'portal_workflow')

    before = wftool.getInfoFor(task, 'review_state')
    before = wftool.getTitleForStateOnType(before, task.Type())

    wftool.doActionFor(task, transition)

    after = wftool.getInfoFor(task, 'review_state')
    after = wftool.getTitleForStateOnType(after, task.Type())

    response.add_change('review_state', _(u'Issue state'),
                        before, after)

    return response

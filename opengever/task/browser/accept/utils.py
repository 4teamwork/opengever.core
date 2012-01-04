from Products.CMFCore.utils import getToolByName
from opengever.task import _
from opengever.task.util import add_simple_response
from persistent.dict import PersistentDict


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


class AcceptTaskSessionDataManager(object):

    KEY = 'accept-task-wizard'

    def __init__(self, request):
        self.request = request
        self.oguid = self.request.get('oguid')
        assert self.oguid, 'Could not find "oguid" in request.'
        self.session = request.SESSION

    def get_data(self):
        if self.KEY not in self.session.keys():
            self.session[self.KEY] = PersistentDict()

        wizard_data = self.session[self.KEY]

        if self.oguid not in wizard_data:
            wizard_data[self.oguid] = PersistentDict()

        return wizard_data[self.oguid]

    def get(self, key, default=None):
        return self.get_data().get(key, default)

    def set(self, key, value):
        return self.get_data().set(key, value)

    def update(self, data):
        self.get_data().update(data)

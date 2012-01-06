from AccessControl import getSecurityManager
from BTrees.OOBTree import OOBTree
from datetime import datetime
from datetime import timedelta
from five import grok
from opengever.ogds.base.utils import remote_request
from opengever.task.interfaces import ISuccessorTaskController
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from zope.app.component.hooks import getSite
from zope.component import getUtility
from zope.interface import Interface
import json


class IAcceptTaskStorageManager(Interface):
    """Provides a storage for storing data used along the wizard steps when
    accepting a task. The data can also by synced to a remote client.
    """

    def get_data(oguid=None, task=None):
        """Returns the data storage of a task identified by either its
        `oguid` or by passing the `task` object.
        """


ANNOTATIONS_KEY = 'accept-task-wizard'
STORAGE_TIMEOUT = 60 * 60 * 24 * 2


class AcceptTaskStorageManager(grok.GlobalUtility):
    grok.implements(IAcceptTaskStorageManager)

    def _get_user_storage(self):
        userid = getSecurityManager().getUser().getId()
        data = IAnnotations(getSite())
        if ANNOTATIONS_KEY not in data.keys():
            data[ANNOTATIONS_KEY] = OOBTree()

        storage = data[ANNOTATIONS_KEY]
        if userid not in storage.keys():
            storage.insert(userid, PersistentDict())

        return storage.get(userid)

    def _cleanup_user_storage(self, user_storage):
        threshold = datetime.now() - timedelta(seconds=STORAGE_TIMEOUT)

        for key in user_storage.keys():
            data = user_storage.get(key)
            if data.get('__created') < threshold:
                del user_storage[key]

    def get_data(self, oguid=None, task=None):
        if not oguid and not task:
            raise TypeError('Either oguid or task required.')

        if oguid and task:
            raise TypeError('Only one of oguid and task can be used.')

        if task:
            oguid = ISuccessorTaskController(task).get_oguid()

        storage = self._get_user_storage()
        self._cleanup_user_storage(storage)

        if oguid not in storage.keys():
            storage[oguid] = PersistentDict()
            storage[oguid]['__created'] = datetime.now()

        return storage[oguid]

    def update(self, data, oguid=None, task=None):
        self.get_data(oguid=oguid, task=task).update(data)

    def get(self, key, oguid=None, task=None, default=None):
        return self.get_data(oguid=oguid, task=task).get(key, default)

    def set(self, key, value, oguid=None, task=None):
        self.get_data(oguid=oguid, task=task)[key] = value

    def push_to_remote_client(self, client_id, oguid):
        data = dict(self.get_data(oguid=oguid))
        del data['__created']

        req_data = {'session-data': json.dumps(data),
                    'oguid': oguid}
        response = remote_request(client_id,
                                  '@@accept_task-receive_storage_data',
                                  data=req_data)

        if response.read().strip() != 'OK':
            raise Exception('Could not push session data to client %s' % (
                    client_id))


class ReceiveAcceptTaskStorageData(grok.View):
    """This view is used to update the session data. The session data manager
    calls this view on a remote client for pushing the data to the target
    client.
    """

    grok.context(Interface)
    grok.name('accept_task-receive_storage_data')
    grok.require('zope2.View')

    def render(self):
        jsondata = self.request.get('session-data')
        oguid = self.request.get('oguid')
        data = json.loads(jsondata)

        getUtility(IAcceptTaskStorageManager).update(data, oguid=oguid)
        return 'OK'

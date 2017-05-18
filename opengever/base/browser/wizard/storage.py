from AccessControl import getSecurityManager
from BTrees.OOBTree import OOBTree
from datetime import datetime
from datetime import timedelta
from five import grok
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.base.request import dispatch_request
from opengever.base.utils import ok_response
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import Interface
import json


ANNOTATIONS_KEY = 'wizard-data-storage'
STORAGE_TIMEOUT = 60 * 60 * 24 * 2


class WizardDataStorage(grok.GlobalUtility):
    grok.implements(IWizardDataStorage)

    def _get_user_storage(self):
        userid = getSecurityManager().getUser().getId()
        data = IAnnotations(getSite())
        if ANNOTATIONS_KEY not in data:
            data[ANNOTATIONS_KEY] = OOBTree()

        storage = data[ANNOTATIONS_KEY]
        if userid not in storage:
            storage.insert(userid, PersistentDict())

        return storage.get(userid)

    def _cleanup_user_storage(self, user_storage):
        threshold = datetime.now() - timedelta(seconds=STORAGE_TIMEOUT)

        for key in user_storage.keys():
            data = user_storage.get(key)
            if data.get('__created') < threshold:
                del user_storage[key]

    def _get_data(self, key):
        storage = self._get_user_storage()
        self._cleanup_user_storage(storage)

        if key not in storage:
            storage[key] = PersistentDict()
            storage[key]['__created'] = datetime.now()

        return storage[key]

    def get_data(self, key):
        """Return a dict copy of our internal PersistentDict.

        The copy is created to:
        - avoid exposing the internal timestamp (could be set as attribute of
          objects created from the data-dict)
        - avoid passing a reference to our internal data to avoid accidental
          modifications

        """
        data = dict(self._get_data(key))
        del data['__created']
        return data

    def drop_data(self, key):
        storage = self._get_user_storage()
        if key in storage:
            del storage[key]

    def update(self, key, data):
        self._get_data(key).update(data)

    def get(self, key, datakey, default=None):
        return self._get_data(key).get(datakey, default)

    def set(self, key, datakey, value):
        self._get_data(key)[datakey] = value

    def push_to_remote_client(self, key, admin_unit_id):
        data = self.get_data(key)

        req_data = {'data-set': json.dumps(data),
                    'key': key}
        response = dispatch_request(admin_unit_id,
                                    '@@receive-wizard-data-set',
                                    data=req_data)

        response_body = response.read()
        if response_body.strip() != 'OK':
            raise Exception('Could not push session data to admin_unit %s' % (
                            admin_unit_id))


class ReceiveWizardDataSet(grok.View):
    """Receives a IWizardDataStorage data set from a remote client and stores
    it on the target client.
    """

    grok.context(Interface)
    grok.name('receive-wizard-data-set')
    grok.require('zope2.View')

    def render(self):
        jsondata = self.request.get('data-set')
        key = self.request.get('key')
        data = json.loads(jsondata)

        getUtility(IWizardDataStorage).update(key, data)

        return ok_response()

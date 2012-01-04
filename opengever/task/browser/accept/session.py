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

class Inbox(object):

    def __init__(self, org_unit):
        self._org_unit = org_unit

    def id(self):
        return 'inbox:{0}'.format(self._org_unit.id())

    def __repr__(self):
        return '<Inbox %s>' % self.id()

    def assigned_users(self):
        return self._org_unit.inbox_group.users

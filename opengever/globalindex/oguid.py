class Oguid(object):

    SEPARATOR = ':'

    def __init__(self, id=None, admin_unit_id=None, intid=None):
        # poor mans XOR
        assert bool(id) != bool(admin_unit_id and intid), \
            'either `oguid` or both, `admin_unit_id` and `intid` must be '\
            'specified'

        if id:
            if isinstance(id, basestring):
                self.id = id
            else:
                # we assume an Oguid instance
                self.id = id.id
        else:
            self._admin_unit_id = admin_unit_id
            self._intid = int(intid)
            self._id = self._join_oguid(admin_unit_id, intid)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value
        self._admin_unit_id, self._intid = self._split_oguid(value)

    @property
    def admin_unit_id(self):
        return self._admin_unit_id

    @admin_unit_id.setter
    def admin_unit_id(self, value):
        self._admin_unit_id = value
        self._id = self._join_oguid(value, self._intid)

    @property
    def intid(self):
        return self._intid

    @intid.setter
    def intid(self, value):
        self._intid = value
        self._id = self._join_oguid(self._admin_unit_id, value)

    def _split_oguid(self, oguid):
        parts = oguid.split(self.SEPARATOR)
        return (parts[0], int(parts[1]),)

    def _join_oguid(self, admin_unit_id, intid):
        return self.SEPARATOR.join((admin_unit_id, str(intid),))

    def __str__(self):
        return self.id

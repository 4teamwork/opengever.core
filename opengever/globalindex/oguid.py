class Oguid(object):

    SEPARATOR = ':'

    def __init__(self, admin_unit_id=None, int_id=None, id=None):
        # poor mans XOR
        assert bool(id) != bool(admin_unit_id and int_id), \
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
            self._int_id = int(int_id)
            self._id = self._join_oguid(admin_unit_id, int_id)

    def __composite_values__(self):
        return (self.admin_unit_id, self.int_id,)

    def __eq__(self, other):
        if isinstance(other, basestring):
            return self.id == other
        return isinstance(other, Oguid) and \
            other.admin_unit_id == self.admin_unit_id and \
            other.int_id == self.int_id

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value
        self._admin_unit_id, self._int_id = self._split_oguid(value)

    @property
    def admin_unit_id(self):
        return self._admin_unit_id

    @admin_unit_id.setter
    def admin_unit_id(self, value):
        self._admin_unit_id = value
        self._id = self._join_oguid(value, self._int_id)

    @property
    def int_id(self):
        return self._int_id

    @int_id.setter
    def int_id(self, value):
        self._int_id = value
        self._id = self._join_oguid(self._admin_unit_id, value)

    def _split_oguid(self, oguid):
        parts = oguid.split(self.SEPARATOR)
        return (parts[0], int(parts[1]),)

    def _join_oguid(self, admin_unit_id, intid):
        return self.SEPARATOR.join((admin_unit_id, str(intid),))

    def __str__(self):
        return self.id

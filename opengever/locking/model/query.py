from opengever.locking.model import Lock
from opengever.locking.model.locks import lowest_valid
from opengever.base.query import BaseQuery


class LockQuery(BaseQuery):

    def valid_locks(self, object_type, object_id):
        query = Lock.query.filter_by(object_type=object_type,
                                     object_id=object_id)
        return query.filter(Lock.time >= lowest_valid())

    def invalid_locks(self):
        return Lock.query.filter(Lock.time < lowest_valid())


Lock.query_cls = LockQuery

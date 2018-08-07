class RecordNotFound(Exception):
    def __init__(self, klass, record_id):
        super(RecordNotFound, self).__init__(
            "no %s found for %s" % (klass.__name__, record_id))
        self.klass = klass
        self.record_id = record_id

from ftw.builder import builder_registry
from opengever.activity import Resource
from opengever.activity import Watcher
from opengever.globalindex.oguid import Oguid
from opengever.ogds.models.tests.builders import SqlObjectBuilder


class ResourceBuilder(SqlObjectBuilder):

    mapped_class = Resource
    id_argument_name = 'resource_id'

    def __init__(self, session):
        super(ResourceBuilder, self).__init__(session)

    def oguid(self, oguid):
        self.arguments['oguid'] = Oguid(id=oguid)
        return self

builder_registry.register('resource', ResourceBuilder)


class WatcherBuilder(SqlObjectBuilder):

    mapped_class = Watcher
    id_argument_name = 'watcher_id'

    def __init__(self, session):
        super(WatcherBuilder, self).__init__(session)

builder_registry.register('watcher', WatcherBuilder)

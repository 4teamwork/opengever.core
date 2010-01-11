
from opengever.examplecontent.handlers import developer
from opengever.examplecontent.handlers import ogds
from opengever.examplecontent.handlers import tree_portlet
from opengever.examplecontent.handlers import pas_create_users

from opengever.examplecontent.utils import GenericContentCreator

HANDLERS = {
    'developer' : developer.setupVarious,
    'ogds' : ogds.SetupVarious(),
    'tree_portlet' : tree_portlet.SetupVarious(),
    }

DYNAMIC_HANDLERS = {
    'pas_create_users' : pas_create_users.SetupVarious(),
    }

def setupVarious(setup):
    SetupHandler(setup)()
    handler = setup.readDataFile('opengever.examplecontent_various.txt')
    if isinstance(handler, str):
        handler = handler.strip()
        if handler in HANDLERS.keys():
            HANDLERS[handler](setup)
    for name, handler in DYNAMIC_HANDLERS.items():
        if handler.active(setup):
            handler(setup)

AUTOCREATE_SOURCE_FILES = [
    'taskoverview.csv',
    'reposystem.csv',
    'regplan.csv',
    ] + ['content%i.csv' % i for i in range(20)]


class SetupHandler(object):

    def __init__(self, setup):
        self.setup = setup
        self.portal = self.setup.getSite()
        self.openDataFile = self.setup.openDataFile

    def __call__(self):
        for filename in AUTOCREATE_SOURCE_FILES:
            if self.openDataFile(filename):
                GenericContentCreator(self.setup).create_from_csv(filename)

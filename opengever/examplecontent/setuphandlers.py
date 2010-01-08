
from opengever.examplecontent.handlers import developer
from opengever.examplecontent.handlers import ogds

from opengever.examplecontent.utils import GenericContentCreator

HANDLERS = {
    'developer' : developer.setupVarious,
    'ogds' : ogds.SetupVarious(),
    }

def setupVarious(setup):
    handler = setup.readDataFile('opengever.examplecontent_various.txt')
    if not isinstance(handler, str):
        return
    else:
        handler = handler.strip()
    if handler in HANDLERS.keys():
        return HANDLERS[handler](setup)
    else:
        return SetupHandler(setup)(handler)

AUTOCREATE_SOURCE_FILES = [
    'taskoverview.csv',
    'reposystem.csv',
    'regplan.csv',
    ]


class SetupHandler(object):

    def __init__(self, setup):
        self.setup = setup
        self.portal = self.setup.getSite()
        self.openDataFile = self.setup.openDataFile

    def __call__(self, filecontent):
        for filename in AUTOCREATE_SOURCE_FILES:
            if self.openDataFile(filename):
                GenericContentCreator(self.setup).create_from_csv(filename)

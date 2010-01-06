
from opengever.examplecontent.handlers import developer
from opengever.examplecontent.handlers import ogds

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

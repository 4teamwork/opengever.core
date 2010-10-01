from collective.transmogrifier.transmogrifier import Transmogrifier
import transaction

def start_import(context):
    transmogrifier = Transmogrifier(context)

    transmogrifier(u'opengever.examplecontent.repository')
    transaction.commit()

    transmogrifier(u'opengever.examplecontent.various')
    transaction.commit()

    # transmogrifier(u'opengever.examplecontent.users')
    # transaction.commit()

def settings(context):
    # exclude items from the navigation we not used 
    context.get('news').setExcludeFromNav(True)
    context.get('news').reindexObject()
    context.get('events').setExcludeFromNav(True)
    context.get('events').reindexObject()
    context.get('Members').setExcludeFromNav(True)
    context.get('Members').reindexObject()
    
    # set default page
    context.default_page = 'ordnungssystem'

def setupVarious(setup):
    
    if setup.readDataFile('opengever.examplecontent.txt') is None:
        pass


    site = setup.getSite()
    start_import(site)
    settings(site)

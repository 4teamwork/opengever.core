from collective.transmogrifier.transmogrifier import Transmogrifier
import transaction

def start_import(context):
    transmogrifier = Transmogrifier(context)

    transmogrifier(u'opengever.examplecontent.repository')
    transaction.commit()

    transmogrifier(u'opengever.examplecontent.various')
    transaction.commit()

    transmogrifier(u'opengever.examplecontent.contacts')
    transaction.commit()

def setupVarious(setup):
    if setup.readDataFile('opengever.examplecontent.txt') is None:
        return
    site = setup.getSite()
    start_import(site)

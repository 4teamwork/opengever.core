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


def installed(site):
    start_import(site)

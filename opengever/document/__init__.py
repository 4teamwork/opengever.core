from zope.i18nmessageid import MessageFactory
import mimetypes

_ = MessageFactory('opengever.document')

mimetypes.add_type('application/vnd.mindjet.mindmanager', '.mmap')

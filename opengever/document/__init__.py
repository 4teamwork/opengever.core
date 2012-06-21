from zope.i18nmessageid import MessageFactory
import mimetypes

_ = MessageFactory('opengever.document')

# MindJet MindManager
mimetypes.add_type('application/vnd.mindjet.mindmanager', '.mmap')
# MS Visio
mimetypes.add_type('application/vnd.visio', '.vsd')
mimetypes.add_type('application/vnd.visio', '.vss')
# Adobe InDesign
mimetypes.add_type('application/x-indesign', '.ind')
mimetypes.add_type('application/x-indesign', '.indd')
# Adobe Photoshop
mimetypes.add_type('image/vnd.adobe.photoshop', '.psd')
# Adobe Illustrator
mimetypes.add_type('application/illustrator', '.ai')
# MS Project
mimetypes.add_type('application/vnd.ms-project', '.mpp')
# MS Project (generic)
mimetypes.add_type('application/x-project', '.mpt')
mimetypes.add_type('application/x-project', '.mpt')
mimetypes.add_type('application/x-project', '.mpv')
mimetypes.add_type('application/x-project', '.mpx')

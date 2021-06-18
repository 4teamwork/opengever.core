from opengever.document.extra_mimetypes import register_additional_mimetypes
from opengever.document.interfaces import IDocumentSettings
from opengever.document.officeconnector import register_ee_filename_callback
from plone.registry.interfaces import IRegistry
from Products.CMFCore.permissions import ManagePortal
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('opengever.document')

DOCUMENTISH_TYPES = ['ftw.mail.mail', 'opengever.document.document',
                     'opengever.meeting.proposaltemplate', 'opengever.meeting.sablontemplate']

# Register some additional well-known MIME types to help server-side file
# format recognition do a better job.
register_additional_mimetypes()

# Register a callback function for ZEM generation in Products.ExternalEditor
# to include a document's filename in the metadata.
register_ee_filename_callback()


def is_watcher_feature_enabled():
    try:
        registry = getUtility(IRegistry)
        return registry.forInterface(IDocumentSettings).watcher_feature_enabled

    except (KeyError, AttributeError):
        return False


def initialize(context):
    """Registers modifiers with zope (on zope startup).
    """
    from opengever.document.modifiers import modifiers

    for m in modifiers:
        context.registerClass(
            m['wrapper'], m['id'],
            permission=ManagePortal,
            constructors=(m['form'], m['factory']),
            icon=m['icon'],
        )


def is_documentish_portal_type(portal_type):
    return portal_type in DOCUMENTISH_TYPES

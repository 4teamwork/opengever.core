from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from opengever.base.marmoset_patch import marmoset_patch
from ZODB.POSException import ConflictError
from ZPublisher.HTTPRequest import FileUpload
import logging


LOGGER = logging.getLogger('opengever.base')


import webdav.LockItem
 # 24 hours
webdav.LockItem.DEFAULTTIMEOUT = 24 * 60 * 60L
LOGGER.info('Monkey patched webdav.LockItem.DEFAULTTIMEOUT')

# --------

from plone.dexterity.content import Container
# Change permission for manage_pasteObjects to "Add portal content"
# See https://dev.plone.org/ticket/9177

# XXX Find a way to do this without patching __ac_permissions__ directly

def drop_protected_attr_from_ac_permissions(attribute, classobj):
    new_mappings = []
    for mapping in Container.__ac_permissions__:
        perm, attrs = mapping
        if not attribute in attrs:
            new_mappings.append(mapping)
        else:
            modified_attrs = tuple([a for a in attrs if not a == attribute])
            modified_mapping = (perm, modified_attrs)
            new_mappings.append(modified_mapping)
    classobj.__ac_permissions__ = tuple(new_mappings)

drop_protected_attr_from_ac_permissions('manage_pasteObjects', Container)
sec = ClassSecurityInfo()
sec.declareProtected(Products.CMFCore.permissions.AddPortalContent,
                    'manage_pasteObjects')
sec.apply(Container)
InitializeClass(Container)

LOGGER.info('Monkey patched plone.dexterity.content.Container')

# --------

# XXX: Patch ftw.mail.inbound.createMailInContainer
# Because `preserved_as_paper` has a schema level default, its default
# value doesn't get set correctly, so we set explicitely after setting
# the defaults.
# TODO: Fix in ftw.mail and remove this monkey patch

from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from Acquisition import aq_inner
from ftw.mail.inbound import set_defaults
from opengever.document.interfaces import IDocumentSettings
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContent
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import queryUtility
from zope.container.interfaces import INameChooser
from zope.schema import getFields
from zope.security.interfaces import IPermission


def createMailInContainer(container, message):
    """Add a mail object to a container.

    The new object, wrapped in its new acquisition context, is returned.
    """

    # lookup the type of the 'message' field and create an instance
    fti = getUtility(IDexterityFTI, name='ftw.mail.mail')
    schema = fti.lookupSchema()
    field_type = getFields(schema)['message']._type
    message_value = field_type(data=message,
                       contentType='message/rfc822', filename=u'message.eml')
    # create mail object
    content = createContent('ftw.mail.mail', message=message_value)

    container = aq_inner(container)
    container_fti = container.getTypeInfo()

    # check permission
    permission = queryUtility(IPermission, name='ftw.mail.AddInboundMail')
    if permission is None:
        raise Unauthorized("Cannot create %s" % content.portal_type)
    if not getSecurityManager().checkPermission(permission.title, container):
        raise Unauthorized("Cannot create %s" % content.portal_type)

    # check addable types
    if container_fti is not None and \
            not container_fti.allowType(content.portal_type):
        raise ValueError("Disallowed subobject type: %s" % (
                content.portal_type))

    normalizer = queryUtility(IIDNormalizer)
    normalized_subject = normalizer.normalize(content.title)

    name = INameChooser(container).chooseName(normalized_subject, content)
    content.id = name

    newName = container._setObject(name, content)
    obj = container._getOb(newName)
    obj = set_defaults(obj, container)

    # ---- patched
    registry = getUtility(IRegistry)
    document_settings = registry.forInterface(IDocumentSettings)
    obj.preserved_as_paper = document_settings.preserved_as_paper_default
    # ---- patched

    obj.reindexObject()
    return obj


from ftw.mail import inbound
inbound.createMailInContainer = createMailInContainer

LOGGER.info('Monkey patched ftw.mail.inbound.createMailInContainer')


# --------
# Monkeypatch for plone.formwidget.namedfile.convert.NamedDataConverter

# To include the fix https://github.com/plone/plone.formwidget.namedfile/pull/9
# which involves in broken files, when uploading documents with firefox.

# This monkeypatch should be removed after updating to
# plone.formwidget.namedfile 1.0.11
from plone.formwidget.namedfile.converter import NamedDataConverter
from plone.namedfile.interfaces import INamed
from plone.namedfile.utils import safe_basename


def toFieldValue(self, value):
    if value is None or value == '':
        return self.field.missing_value

    if INamed.providedBy(value):
        return value
    elif isinstance(value, FileUpload):

        filename = safe_basename(value.filename)

        if filename is not None and not isinstance(filename, unicode):
            # Work-around for
            # https://bugs.launchpad.net/zope2/+bug/499696
            filename = filename.decode('utf-8')

        value.seek(0)
        data = value.read()
        if data or filename:
            return self.field._type(data=data, filename=filename)
        else:
            return self.field.missing_value

    else:
        return self.field._type(data=str(value))


NamedDataConverter.toFieldValue = toFieldValue
LOGGER.info(
    'Monkey patched '
    'plone.formwidget.namedfile.converter.NamedDataConverter.toFieldValue')


# --------
# Monkeypatch `OFS.CopySupport.CopyContainer._verifyObjectPaste`
# to disable `Delete objects` permission check when moving items

from Acquisition import aq_parent
from App.Dialogs import MessageDialog
from cgi import escape
from OFS.CopySupport import absattr
from OFS.CopySupport import CopyContainer
from OFS.CopySupport import CopyError


def _verifyObjectPaste(self, object, validate_src=1):
    # Verify whether the current user is allowed to paste the
    # passed object into self. This is determined by checking
    # to see if the user could create a new object of the same
    # meta_type of the object passed in and checking that the
    # user actually is allowed to access the passed in object
    # in its existing context.
    #
    # Passing a false value for the validate_src argument will skip
    # checking the passed in object in its existing context. This is
    # mainly useful for situations where the passed in object has no
    # existing context, such as checking an object during an import
    # (the object will not yet have been connected to the acquisition
    # heirarchy).

    if not hasattr(object, 'meta_type'):
        raise CopyError(MessageDialog(
              title   = 'Not Supported',
              message = ('The object <em>%s</em> does not support this' \
                         ' operation' % escape(absattr(object.id))),
              action  = 'manage_main'))

    if not hasattr(self, 'all_meta_types'):
        raise CopyError(MessageDialog(
              title   = 'Not Supported',
              message = 'Cannot paste into this object.',
              action  = 'manage_main'))

    method_name = None
    mt_permission = None
    meta_types = absattr(self.all_meta_types)

    for d in meta_types:
        if d['name'] == object.meta_type:
            method_name = d['action']
            mt_permission = d.get('permission')
            break

    if mt_permission is not None:
        sm = getSecurityManager()

        if sm.checkPermission(mt_permission, self):
            if validate_src:
                # Ensure the user is allowed to access the object on the
                # clipboard.
                try:
                    parent = aq_parent(aq_inner(object))
                except ConflictError:
                    raise
                except Exception:
                    parent = None

                if not sm.validate(None, parent, None, object):
                    raise Unauthorized(absattr(object.id))

                # --- Patch ---
                # Disable checking for `Delete objects` permission

                # if validate_src == 2: # moving
                #     if not sm.checkPermission(delete_objects, parent):
                #         raise Unauthorized('Delete not allowed.')

                # --- End Patch ---
        else:
            raise CopyError(MessageDialog(
                title = 'Insufficient Privileges',
                message = ('You do not possess the %s permission in the '
                           'context of the container into which you are '
                           'pasting, thus you are not able to perform '
                           'this operation.' % mt_permission),
                action = 'manage_main'))
    else:
        raise CopyError(MessageDialog(
            title = 'Not Supported',
            message = ('The object <em>%s</em> does not support this '
                       'operation.' % escape(absattr(object.id))),
            action = 'manage_main'))

CopyContainer._verifyObjectPaste = _verifyObjectPaste
LOGGER.info('Monkey patched OFS.CopySupport.CopyContainer._verifyObjectPaste')


# --------
# Marmoset patch `plone.app.upgrade.v43.betas.to43rc1` to delay an expensive
# upgrade. The upgrade is re-defined as opengever.policy.base.to4504.


from plone.app.upgrade.v43 import betas


def nullupgrade(context):
    pass

marmoset_patch(betas.to43rc1, nullupgrade)
LOGGER.info('Marmoset patched plone.app.upgrade.v43.betas.to43rc1')


# --------
# Monkey patch the regex used to replace relative paths in url() statements
# with absolute paths in the portal_css tool.
# This has been fixed as of release 3.0.3 of Products.ResourceRegistries
# which is only available for Plone 5.
# See https://github.com/plone/Products.ResourceRegistries/commit/4f9094919bc1c50404e74c748b067a3563e640aa

import re
from Products.ResourceRegistries import utils


utils.URL_MATCH = re.compile(r'''(url\s*\(\s*['"]?)(?!data:)([^'")]+)(['"]?\s*\))''', re.I | re.S)


LOGGER.info('Monkey patched Products.ResourceRegistries.utils.URL_MATCH regexp')


# --------
# Patch for Products.CMFEditions.historyidhandlertool
#           .HistoryIdHandlerTool.register
#
# The default "register" method uses the Products.CMFUid IUniqueIdGenerator
# utility for generating the history ID. This utility uses the auto-increment
# strategy, which generates a lot of conflicts.
#
# In order to reduce the conflicts when generating the history id,
# we switch to the uuid4 implementation, generating a random number instead
# and thus not writing to the same place.

from Products.CMFEditions.historyidhandlertool import HistoryIdHandlerTool
from uuid import uuid4


def HistoryIdHandlerTool_register(self, obj):
    uid = self.queryUid(obj, default=None)
    if uid is None:
        # generate a new unique id and set it
        uid = uuid4().int
        self._setUid(obj, uid)

    return uid


HistoryIdHandlerTool.register = HistoryIdHandlerTool_register
LOGGER.info('Monkey patched Products.CMFEditions.historyidhandlertool'
            '.HistoryIdHandlerTool.register')

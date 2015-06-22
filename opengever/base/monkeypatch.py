"""
Filename with umlauts are not supported yet, so we need to patch that.
Therefore we need to patch:
* Products.Five.browser.decode.processInputs
Filenames of FileUpload objects should be converted to unicode as well
* plone.formwidget.namedfile.widget.filename_encoded
Urllib has a problem with filename, which is now unicode and not utf8
any more. So we need to convert it back to utf8 for urllib.
patched for: plone.formwidget.namedfile == 1.0b2

For further details see:
* https://extranet.4teamwork.ch/projects/opengever-kanton-zug/sprint-backlog/111
* http://code.google.com/p/dexterity/issues/detail?id=101
* https://bugs.launchpad.net/zope2/+bug/499696
"""

from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from Products.Five.browser import decode
from ZPublisher.HTTPRequest import FileUpload
from ZPublisher.HTTPRequest import isCGI_NAMEs
import logging
import time
import urllib


LOGGER = logging.getLogger('opengever.base')


def compute_timezone_for_log():
    """Patched version of http_server's compute_timezone_for_log
    that correctly determines whether it's currently daylight savings time
    or not.
    """

    def is_dst():
        return time.localtime().tm_isdst

    if is_dst():
        tz = time.altzone
    else:
        tz = time.timezone
    if tz > 0:
        neg = 1
    else:
        neg = 0
        tz = -tz
    h, rem = divmod (tz, 3600)
    m, rem = divmod (rem, 60)

    if neg:
        return '-%02d%02d' % (h, m)
    else:
        return '+%02d%02d' % (h, m)

# Patch both the ZServer.medusa.http_server.compute_timezone_for_log
# function and the `tz_for_log` module global to fix the timezone
# used in Z2 logs.

from ZServer.medusa import http_server

http_server.compute_timezone_for_log = compute_timezone_for_log
LOGGER.info('Monkey patched ZServer.medusa.http_server.compute_timezone_for_log')

http_server.tz_for_log = compute_timezone_for_log()
LOGGER.info('Monkey patched ZServer.medusa.http_server.tz_for_log')


# --------


def processInputs(request, charsets=None):
    if charsets is None:
        envadapter = decode.IUserPreferredCharsets(request)
        charsets = envadapter.getPreferredCharsets() or ['utf-8']

    for name, value in request.form.items():
        if not (name in isCGI_NAMEs or name.startswith('HTTP_')):
            if isinstance(value, str):
                request.form[name] = decode._decode(value, charsets)
            elif isinstance(value, list):
                request.form[name] = [decode._decode(val, charsets)
                                       for val in value
                                       if isinstance(val, str)]
            elif isinstance(value, tuple):
                request.form[name] = tuple([decode._decode(val, charsets)
                                             for val in value
                                             if isinstance(val, str)])
            # new part
            elif isinstance(
                value, FileUpload) and isinstance(value.filename, str):
                value.filename = decode._decode(value.filename, charsets)
            # / new part


decode.processInputs = processInputs
LOGGER.info('Monkey patched Products.Five.browser.decode.processInputs')


# --------
class Foo(object):
    @property
    def filename_encoded(self):
        filename = self.filename
        # new part
        if isinstance(filename, unicode):
            filename = filename.encode('utf8')
        # / new part
        if filename is None:
            return None
        else:
            return urllib.quote_plus(filename)

from plone.formwidget.namedfile import widget
setattr(widget.NamedFileWidget,
        'filename_encoded',
        Foo.filename_encoded)
LOGGER.info('Monkey patched plone.formwidget.namedfile.widget.'
            'NameFileWidget.filename_encoded')

# --------

import Products.LDAPUserFolder

Products.LDAPUserFolder.utils.encoding = 'utf-8'
LOGGER.info('Monkey patched Products.LDAPUserFolder.utils.encoding (utf-8)')


# --------

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
                       contentType=u'message/rfc822', filename=u'message.eml')
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
                except:
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

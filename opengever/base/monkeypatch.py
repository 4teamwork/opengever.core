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
import urllib


LOGGER = logging.getLogger('opengever.base')


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

# Patch DexterityContent.__getattr__
# This is required to support dynamic lookup of schema-level default
# values for fields in behaviors. It's basically a backport
# of this Dexterity 2.x fix:
# https://github.com/plone/plone.dexterity/commit/dd491480b869bbe21ee50ef413c263705af7b170

from copy import deepcopy

def DexterityContent_getattr(self, name):
    from plone.dexterity.schema import SCHEMA_CACHE

    # optimization: sometimes we're asked for special attributes
    # such as __conform__ that we can disregard (because we
    # wouldn't be in here if the class had such an attribute
    # defined).
    if name.startswith('__'):
        raise AttributeError(name)

    # attribute was not found; try to look it up in the schema and return
    # a default
    schema = SCHEMA_CACHE.get(self.portal_type)
    if schema is not None:
        field = schema.get(name, None)
        if field is not None:
            return deepcopy(field.default)

    # do the same for each subtype
    for schema in SCHEMA_CACHE.subtypes(self.portal_type):
        field = schema.get(name, None)
        if field is not None:
            return deepcopy(field.default)

    raise AttributeError(name)

from plone.dexterity.content import DexterityContent
from plone.dexterity.content import Item
DexterityContent.__getattr__ = DexterityContent_getattr
Item.__getattr__ = DexterityContent_getattr

LOGGER.info('Monkey patched plone.dexterity.content.DexterityContent')

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
# Monkeypatch for plone.formwidget.namedfile.convert.NamedDataConverter

# To include the fix https://github.com/plone/plone.formwidget.namedfile/pull/9
# which involves in broken files, when uploading documents with firefox.

# Monkeypath should be removed after updating opengever to plone 4.3.
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
LOGGER.info('Monkey patched '
            'plone.formwidget.namedfile.converter.NamedDataConverter.toFieldValue')

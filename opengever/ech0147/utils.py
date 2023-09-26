from opengever.document.document import IDocumentSchema
from opengever.document.subscribers import set_digitally_available
from opengever.ech0147.mappings import INV_CLASSIFICATION_MAPPING
from opengever.ech0147.mappings import INV_PRIVACY_LAYER_MAPPING
from opengever.ech0147.mappings import INV_PUBLIC_TRIAL_MAPPING
from opengever.ech0147.serializer import ECH0147Serializer
from plone.dexterity.utils import safe_utf8
from plone.restapi.interfaces import IDeserializeFromJson
from Products.CMFPlone.utils import safe_unicode
from random import randint
from zope.component import queryMultiAdapter
from zope.container.interfaces import INameChooser
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
import json
import os.path
import re
import transaction
import unicodedata


consecutive_whitespace_pattern = re.compile(" {2,}")


def normalize_filename(string):
    """A python zipfile provides file information by filename: zipfile.NameToInfo

    This function normalizes a given string to our default NFC-format
    and returns a utf-8 encoded string.

    """
    return unicodedata.normalize('NFC', safe_unicode(string)).encode('utf-8')


def get_path_mapping(zipfile):
    """The file-list of a python zipfile can be provided as unicode or as
    utf-8 in the NFD-normal form
    (See: https://docs.python.org/2/library/unicodedata.html#unicodedata.normalize)

    In addition, the zipfile.namelist() returns the real file names which can contain
    consecutive whitespacesit, but the ech-0147 standard defines the pathFileName
    as an xs:token which provides a string without consecutive whitespaces.

    https://www.data2type.de/xml-xslt-xslfo/xml-schema/datentypen-referenz/xs-token/

    This makes it hard to lookup the files in the zip-file.

    To be able to properly lookup the files, we'll create a path mapping which
    maps normalized paths in the format:

    utf-8 strings in the NFC-normal form without consecutive whitespaces to
    the real underlying file path within the zipfile.
    """
    return {
        normalize_filename(consecutive_whitespace_pattern.sub(' ', path)): path
        for path in zipfile.namelist()
    }


def sanitize_metadata(metadata):
    """We do a JSON serialization cycle to get rid of any XML data types."""
    return json.loads(json.dumps(metadata, cls=ECH0147Serializer), cls=ECH0147Serializer)


def create_dossier(container, dossier, zipfile, responsible):
    temp_id = 'dossier.temp.{}'.format(randint(0, 999999))
    id_ = container.invokeFactory(
        'opengever.dossier.businesscasedossier', temp_id)
    obj = container[id_]

    # Mandatory metadata
    metadata = {
        'title': dossier.titles.title[0].value(),
        'responsible': responsible,
    }

    # Optional metadata
    if dossier.openingDate is not None:
        metadata['start'] = dossier.openingDate

    if dossier.classification is not None:
        metadata['classification'] = INV_CLASSIFICATION_MAPPING.get(
            dossier.classification)
    if dossier.hasPrivacyProtection is not None:
        metadata['privacy_layer'] = INV_PRIVACY_LAYER_MAPPING.get(
            dossier.hasPrivacyProtection)

    if dossier.keywords is not None:
        metadata['keywords'] = [k.value() for k in dossier.keywords.keyword]

    if dossier.comments is not None:
        metadata['comments'] = u'\n'.join(
            [k.value() for k in dossier.comments.comment])

    deserializer = queryMultiAdapter((obj, obj.REQUEST), IDeserializeFromJson)
    deserializer(validate_all=True, data=sanitize_metadata(metadata), create=True)

    # Rename dossier
    chooser = INameChooser(container)
    name = chooser.chooseName(None, obj)
    transaction.savepoint(optimistic=True)
    container.manage_renameObject(obj.getId(), name)

    if dossier.dossiers:
        for subdossier in dossier.dossiers.dossier:
            create_dossier(obj, subdossier, zipfile, responsible)

    if dossier.documents:
        for document in dossier.documents.document:
            create_document(obj, document, zipfile)


def create_document(container, document, zipfile):
    path_mapping = get_path_mapping(zipfile)
    temp_id = 'document.temp.{}'.format(randint(0, 999999))
    id_ = container.invokeFactory(
        'opengever.document.document', temp_id)
    obj = container[id_]

    # Mandatory metadata
    metadata = {
        'title': document.titles.title[0].value(),
    }

    # Optional metadata
    if document.openingDate is not None:
        metadata['document_date'] = document.openingDate
    if document.owner is not None:
        metadata['document_author'] = document.owner
    if document.ourRecordReference is not None:
        metadata['foreign_reference'] = document.ourRecordReference

    if document.classification is not None:
        metadata['classification'] = INV_CLASSIFICATION_MAPPING.get(
            document.classification)
    if document.hasPrivacyProtection is not None:
        metadata['privacy_layer'] = INV_PRIVACY_LAYER_MAPPING.get(
            document.hasPrivacyProtection)
    if document.openToThePublic is not None:
        metadata['public_trial'] = INV_PUBLIC_TRIAL_MAPPING.get(
            document.openToThePublic)

    if document.keywords:
        metadata['keywords'] = [k.value() for k in document.keywords.keyword]

    deserializer = queryMultiAdapter((obj, obj.REQUEST), IDeserializeFromJson)
    deserializer(validate_all=True, data=sanitize_metadata(metadata), create=True)

    if document.files:
        file_ = document.files.file[0]
        file_path = path_mapping.get(safe_utf8(file_.pathFileName))
        try:
            zipinfo = zipfile.getinfo(file_path)
        except KeyError:
            # This error is generally raised if a file is referenced in the
            # .xml file but does not exist in the zipfile.
            #
            # Another known reason for this case is a path normalization done by pyxb
            # which changes the given path in the .xml file. Thus the file itself
            # can no longer be found.
            # See https://github.com/4teamwork/opengever.core/pull/7720#issuecomment-1539660053
            raise ValueError('Missing file {}'.format(file_path or file_.pathFileName))

        file_field = IDocumentSchema['file']
        filename = os.path.basename(file_.pathFileName)
        obj.file = file_field._type(
            data=zipfile.read(zipinfo),
            contentType=str(file_.mimeType),
            filename=filename)

    # Rename document
    chooser = INameChooser(container)
    name = chooser.chooseName(None, obj)
    transaction.savepoint(optimistic=True)

    container.manage_renameObject(obj.getId(), name)

    # work around possible event handler ordering issue
    set_digitally_available(obj, None)
    # fire final modified event after rename to make sure bumblebee trigger
    # storing views/handlers use correct document url
    notify(ObjectModifiedEvent(obj))

from opengever.document.document import IDocumentSchema
from opengever.document.subscribers import set_digitally_available
from opengever.ech0147.mappings import INV_CLASSIFICATION_MAPPING
from opengever.ech0147.mappings import INV_PRIVACY_LAYER_MAPPING
from opengever.ech0147.mappings import INV_PUBLIC_TRIAL_MAPPING
from plone.restapi.interfaces import IDeserializeFromJson
from pyxb.binding.datatypes import date as pyxb_date
from random import randint
from zope.component import queryMultiAdapter
from zope.container.interfaces import INameChooser
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
import os.path
import transaction


def convert_dates(data):
    """convert pyxb dates to real python datetime dates, otherwise field
    validation for date fields will raise.
    """

    for key, value in data.items():
        if isinstance(value, pyxb_date):
            data[key] = value.date()


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

    convert_dates(metadata)

    deserializer = queryMultiAdapter((obj, obj.REQUEST),
                                     IDeserializeFromJson)
    deserializer(validate_all=True, data=metadata, create=True)

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

    convert_dates(metadata)

    deserializer = queryMultiAdapter((obj, obj.REQUEST),
                                     IDeserializeFromJson)
    deserializer(validate_all=True, data=metadata, create=True)

    if document.files:
        file_ = document.files.file[0]
        try:
            zipinfo = zipfile.getinfo(file_.pathFileName)
        except KeyError:
            raise ValueError('Missing file {}'.format(file_.pathFileName))

        file_field = IDocumentSchema['file']
        filename = os.path.basename(file_.pathFileName)
        obj.file = file_field._type(
            data=zipfile.read(zipinfo),
            contentType=file_.mimeType,
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

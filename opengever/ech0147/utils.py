from opengever.document.document import IDocumentSchema
from opengever.ech0147.mappings import INV_CLASSIFICATION_MAPPING
from opengever.ech0147.mappings import INV_PRIVACY_LAYER_MAPPING
from opengever.ech0147.mappings import INV_PUBLIC_TRIAL_MAPPING
from plone.restapi.interfaces import IDeserializeFromJson
from random import randint
from zope.component import queryMultiAdapter
from zope.container.interfaces import INameChooser

import transaction
import os.path


def create_dossier(container, dossier, zipfile, responsible):
    temp_id = 'dossier.temp.{}'.format(randint(0, 999999))
    id_ = container.invokeFactory(
        'opengever.dossier.businesscasedossier', temp_id)
    obj = container[id_]

    data = {
        'title': dossier.titles.title[0].value(),
        'start': dossier.openingDate,
        'classification': INV_CLASSIFICATION_MAPPING.get(
            dossier.classification),
        'privacy_layer': INV_PRIVACY_LAYER_MAPPING.get(
            dossier.hasPrivacyProtection),
        'responsible': responsible,
    }
    if dossier.keywords:
        data.update({
            'keywords': [k.value() for k in dossier.keywords.keyword]})

    deserializer = queryMultiAdapter((obj, obj.REQUEST),
                                     IDeserializeFromJson)
    deserializer(validate_all=True, data=data)

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

    data = {
        'title': document.titles.title[0].value(),
        'classification': INV_CLASSIFICATION_MAPPING.get(
            document.classification),
        'privacy_layer': INV_PRIVACY_LAYER_MAPPING.get(
            document.hasPrivacyProtection),
        'document_date': document.openingDate,
        'document_author': document.owner,
        'foreign_reference': document.ourRecordReference,
    }
    if document.keywords:
        data.update({
            'keywords': [k.value() for k in document.keywords.keyword]})

    public_trial = INV_PUBLIC_TRIAL_MAPPING.get(document.openToThePublic)
    if public_trial is not None:
        data.update({'public_trial': public_trial})

    deserializer = queryMultiAdapter((obj, obj.REQUEST),
                                     IDeserializeFromJson)
    deserializer(validate_all=True, data=data)

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

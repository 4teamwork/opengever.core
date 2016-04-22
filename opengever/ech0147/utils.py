from opengever.dossier.behaviors.dossier import IDossier
from random import randint
from zope.container.interfaces import INameChooser
from opengever.document.document import IDocumentSchema
import hashlib
import transaction
import os.path


def file_checksum(filename, chunksize=65536):
    """Calculates a checksum for the given file."""
    h = hashlib.md5()
    with open(filename, 'rb') as f:
        chunk = f.read(chunksize)
        while len(chunk) > 0:
            h.update(chunk)
            chunk = f.read(chunksize)
        return u'MD5', h.hexdigest()


def create_dossier(container, dossier, zipfile):
    temp_id = 'dossier.temp.{}'.format(randint(0, 999999))
    id_ = container.invokeFactory(
        'opengever.dossier.businesscasedossier', temp_id)
    obj = container[id_]

    obj.title = dossier.titles.title[0].value()

    dossier_obj = IDossier(obj)
    dossier_obj.start = dossier.openingDate

    # Rename dossier
    chooser = INameChooser(container)
    name = chooser.chooseName(None, obj)
    transaction.savepoint(optimistic=True)
    container.manage_renameObject(obj.getId(), name)

    if dossier.dossiers:
        for subdossier in dossier.dossiers.dossier:
            create_dossier(obj, subdossier, zipfile)

    if dossier.documents:
        for document in dossier.documents.document:
            create_document(obj, document, zipfile)


def create_document(container, document, zipfile):
    temp_id = 'document.temp.{}'.format(randint(0, 999999))
    id_ = container.invokeFactory(
        'opengever.document.document', temp_id)
    obj = container[id_]

    obj.title = document.titles.title[0].value()

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

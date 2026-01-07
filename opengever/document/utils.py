from opengever.document.interfaces import IDocumentSettings
from plone import api


def is_save_as_pdf_feature_enabled():
    return api.portal.get_registry_record('is_save_document_as_pdf_feature_enabled', interface=IDocumentSettings)   # noqa

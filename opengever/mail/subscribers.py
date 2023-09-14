from opengever.base.utils import unrestrictedUuidToObject
from opengever.document.behaviors.related_docs import IRelatedDocuments
from opengever.document.subscribers import resolve_document_author
from opengever.mail.interfaces import IExtractedFromMail
from opengever.mail.mail import IOGMailMarker
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.interface import noLongerProvides


def set_digitally_available(mail, event):
    """Set the `digitally_available` field upon creation
    (always True for mails by definition).
    """
    mail.digitally_available = True


def resolve_mail_author(mail, event):
    """When mail edited, the author can be specified by userid and should
    be mapped to user fullname. This is not fired upon mail creation,
    as the author is taken from the sender E-mail address in that case."""
    resolve_document_author(mail, event)


def extracted_attachment_deleted(doc, event):
    # Skip plone site removals. Unfortunately no deletion-order seems to be
    # guaranteed, when removing the plone site, so unexpected behaviors can
    # happen, notably that doc will not provide IRelatedDocuments anymore and
    # hence cannot be adapted.
    if IPloneSiteRoot.providedBy(event.object):
        return

    uid = IUUID(doc)
    for related_item in IRelatedDocuments(doc).relatedItems:
        related_obj = related_item.to_object
        if not IOGMailMarker.providedBy(related_obj):
            continue

        for info in related_obj.get_attachments():
            if info.get("extracted_document_uid") == uid:
                related_obj._modify_attachment_info(
                    info.get("position"),
                    extracted=False,
                    extracted_document_uid=None)
                return


def mail_deleted(doc, event):
    """Documents extracted from mails are marked with the IExtractedFromMail
    interface. This interface should be removed if the corresponding mail
    is deleted.
    """
    # Skip plone site removals. Unfortunately no deletion-order seems to be
    # guaranteed, when removing the plone site, so unexpected behaviors can
    # happen.
    if IPloneSiteRoot.providedBy(event.object):
        return

    for info in doc.get_attachments():
        if not info.get('extracted'):
            continue
        extracted_doc = unrestrictedUuidToObject(info.get('extracted_document_uid'))
        # When deleting the dossier, it can happen that the extracted doc
        # was already deleted
        if extracted_doc:
            noLongerProvides(extracted_doc, IExtractedFromMail)

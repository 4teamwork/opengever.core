from opengever.document.behaviors.related_docs import IRelatedDocuments
from opengever.document.subscribers import resolve_document_author
from opengever.mail.exceptions import SourceMailNotFound
from opengever.mail.mail import IOGMailMarker
from plone.uuid.interfaces import IUUID
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent


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


def find_corresponding_mail_info_in_write_modus(doc):
    uid = IUUID(doc)
    for related_item in IRelatedDocuments(doc).relatedItems:
        related_obj = related_item.to_object
        if not IOGMailMarker.providedBy(related_obj):
            continue

        for info in related_obj.get_attachments():
            if info.get("extracted_document_uid") == uid:
                write_info = related_obj._get_attachment_info(
                    info.get("position"), write_modus=True)
                return write_info
    raise SourceMailNotFound("Source Mail not found when Extracted attachment moved.")


def extracted_attachment_moved(doc, event):
    """Mails keep track of their attachments extracted to documents.
    When such a document is moved, the corresponding information has to
    be updated on the Mail."""

    # Since IObjectAddedEvent and IObjectRemovedEvent subclasses
    # IObjectMovedEvent this event handler is also called for
    # IObjectAddedEvent and IObjectRemovedEvent but we should not
    # do anything in these cases.
    if IObjectAddedEvent.providedBy(event) or IObjectRemovedEvent.providedBy(event):
        return

    write_info = find_corresponding_mail_info_in_write_modus(doc)
    write_info["extracted_document_url"] = doc.absolute_url()


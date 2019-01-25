from opengever.document.subscribers import resolve_document_author


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

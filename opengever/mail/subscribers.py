def set_digitally_available(mail, event):
    """Set the `digitally_available` field upon creation
    (always True for mails by definition).
    """
    mail.digitally_available = True

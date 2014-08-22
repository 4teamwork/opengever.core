from five import grok
from ftw.mail.mail import IMail
from zope.lifecycleevent.interfaces import IObjectCreatedEvent


@grok.subscribe(IMail, IObjectCreatedEvent)
def set_digitally_available(mail, event):
    """Set the `digitally_available` field upon creation
    (always True for mails by definition).
    """
    mail.digitally_available = True

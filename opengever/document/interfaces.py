from zope import schema
from zope.component.interfaces import IObjectEvent
from zope.interface import Interface


# custom plone.formwidget.namedfile modes
NO_DOWNLOAD_DISPLAY_MODE = 'no_download_display'
NO_DOWNLOAD_INPUT_MODE = 'no_download_input'


class IObjectCheckedOutEvent(IObjectEvent):
    """ Event interface for events.ObjectCheckedOutEvent
    """
    comment = schema.Text(title=u'journal comment')


class IObjectCheckedInEvent(IObjectEvent):
    """ Event interface for events.ObjectCheckedInEvent
    """
    comment = schema.Text(title=u'journal comment')


class IObjectBeforeCheckInEvent(IObjectEvent):
    """ Event interface for events.ObjectBeforeCheckInEvent
    """


class IObjectCheckoutCanceledEvent(IObjectEvent):
    """ Event interface for events.ObjectCheckoutCanceledEvent
    """


class IObjectRevertedToVersion(IObjectEvent):
    """The object was reverted back to a specific version.
    """


class IFileCopyDownloadedEvent(IObjectEvent):
    """ Event interface for event.FileDownloadedEvent
    """


class IDocumentType(Interface):
    document_types = schema.List(
        title=u"Document Type",
        value_type=schema.Choice(
            title=u"Name",
            vocabulary=u'opengever.document.document_types',
        ),
    )


PRESERVED_AS_PAPER_DEFAULT = True


class IDocumentSettings(Interface):
    """Registry interface with general document settings."""

    preserved_as_paper_default = schema.Bool(
        title=u"Client default for preserved_as_paper",
        default=PRESERVED_AS_PAPER_DEFAULT,
    )


class ICheckinCheckoutManager(Interface):
    """Interface for the checkin / checkout manager.
    """

    def get_checked_out_by():
        """If the document is checked out, this method returns the userid
        of the user who has checked out the document, otherwise it
        returns `None`.
        """

    def is_checkout_allowed():
        """Checks whether checkout is allowed for the current user on the
        adapted document.
        """

    def checkout():
        """Checkout the adapted document.
        """

    def is_checked_out_by_current_user():
        """Returns True if the document is checked out by the currently
        logged in user otherwise False.
        """

    def is_checkin_allowed():
        """Checks whether checkin is allowed for the current user on the
        adapted document.
        """

    def checkin(comment=None):
        """Checkin the adapted document, using the `comment` for the
        journal entry.
        """

    def is_cancel_allowed():
        """Checks whether the user is able to cancel a checkout.
        """

    def cancel():
        """Cancel the current checkout.
        """


class IDocumentIndexer(Interface):
    """Describes an adapter that is able to extract plain text from files
    contained in opengever.document.document objects.
    """

    def extract_text():
        """Extract plain text from the adapted document.
        """


class INoAutomaticInitialVersion(Interface):
    """Request layer to disable automatic creation of initial versions
    via event handler.

    This is sometimes necessary when a transmogrifier pipeline is involved,
    i.e. during setup or migration.
    """

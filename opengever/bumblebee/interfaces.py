from zope import schema
from zope.interface import Attribute
from zope.interface import Interface
from zope.component.interfaces import IObjectEvent


class IPDFDownloadedEvent(IObjectEvent):
    """Fired when the converted PDF for an object is downloaded from bumblebee.
    """


class IGeverBumblebeeSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable bumblebee feature',
        description=u'Whether features from opengever.bumblebee are enabled',
        default=False)

    open_pdf_in_a_new_window = schema.Bool(
        title=u'Open PDF in a new window/tab.',
        description=u'Sets target="_blank" for links to PDF files.',
        default=False)

    is_auto_refresh_enabled = schema.Bool(
        title=u'Enable bumblebee auto refresh feature',
        description=u'Automatically load preview images once available.',
        default=False)


class IVersionedContextMarker(Interface):
    """Marker interface for a versioned context.
    """


class IBumblebeeOverlay(Interface):
    """Interface for the bumblebee overlay.

    This interface defines the required methods to render the bumblebee
    overlay template.
    """

    version_id = Attribute(
        "Defines which version of the file should be shown."
        "Default: None => the actual file will be shown")

    def preview_pdf_url():
        """Returns an url to an image.

        This can be either the url to the bumblebee preview image
        or the url to a fallabck-image.
        """

    def get_mime_type_css_class():
        """Returns the mime-type css class as a string.
        """

    def get_file_size():
        """Returns a string with the filesize in kb.
        If there is no file, it returns None.
        """

    def get_creator_link():
        """Returns an html-link to the creator of the object.
        """

    def get_document_date():
        """Returns the localized document date.
        """

    def get_containing_dossier():
        """Returns the containing dossier as an object.
        """

    def get_sequence_number():
        """Returns the sequence number as integer or string.

        If there is no sequence_number it returns None
        """

    def get_reference_number():
        """Returns the reference number as a string.

        If there is no reference number it returns None
        """

    def has_file():
        """Returns True if the object contains a file.

        It returns False, if there is no file.
        """

    def get_file():
        """Returns the file-object if there is a file.

        Returns None if there is no file.
        """

    def render_checked_out_viewlet():
        """Renders the checked out viewlet.

        Returns html.
        """

    def render_lock_info_viewlet():
        """Renders the lock info viewlet.

        Returns html.
        """

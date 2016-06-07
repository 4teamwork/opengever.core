from zope import schema
from zope.interface import Interface


class IGeverBumblebeeSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable bumblebee feature',
        description=u'Whether features from opengever.bumblebee are enabled',
        default=False)


class IBumblebeeOverlay(Interface):
    """Interface for the bumblebee overlay.

    This interface defines the required methods to render the bumblebee
    overlay template.
    """

    def get_preview_pdf_url():
        """Returns an url to an image.

        This can be either the url to the bumblebee preview image
        or the url to a fallabck-image.
        """

    def get_mime_type_css_class():
        """Returns the mime-type css class as a string.
        """

    def get_file_title():
        """Returns the title of the file.
        If there is no file, it returns None.
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

    def get_checkout_url():
        """Returns the url to checkout the file.

        Returns None if it's not possible to checkout the file.
        """

    def get_download_copy_link():
        """Returns the html-link to download a copy of the file.

        Returns None if its not possible to download a copy.
        """

    def get_open_as_pdf_url():
        """Returns the url to open the file as a pdf representation.

        If there is no pdf-representation, it returns None
        """

    def get_edit_metadata_url():
        """Returns the url to edit the metadata of the current object.
        """

    def get_detail_view_url():
        """Returns the url to the base-view of the current object.
        """

    def get_checkin_without_comment_url():
        """Returns the url to checkin the file.

        Returns None if it's not possible to checkin the file.
        """

    def get_checkin_with_comment_url():
        """Returns the url to checkin the file with a comment.

        Returns None if it's not possible to checkin the file.
        """

    def has_file():
        """Returns True if the object contains a file.

        It returns False, if there is no file.
        """

    def get_file():
        """Returns the file-object if there is a file.

        Returns None if there is no file.
        """

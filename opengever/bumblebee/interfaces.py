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
        """
        """

    def get_mime_type_css_class():
        """
        """

    def get_file_title():
        """
        """

    def get_file_size():
        """
        """

    def get_creator_link():
        """
        """

    def get_document_date():
        """
        """

    def get_containing_dossier():
        """
        """

    def get_sequence_number():
        """
        """

    def get_reference_number():
        """
        """

    def get_checkout_url():
        """
        """

    def get_download_copy_link():
        """
        """

    def get_open_as_pdf_link():
        """
        """

    def get_edit_metadata_url():
        """
        """

    def get_detail_view_url():
        """
        """

    def get_checkin_without_comment_url():
        """
        """

    def get_checkin_with_comment_url():
        """
        """

    def has_file():
        """
        """

    def get_file():
        """
        """

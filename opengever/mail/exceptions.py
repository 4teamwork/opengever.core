
class AlreadyExtractedError(Exception):
    """Attachment already extracted from Mail.
    """
    message = "Attachment at position {} has already been extracted to {}."

    def __init__(self, info):
        super(AlreadyExtractedError, self).__init__(self.message.format(
            info.get('position'), info.get('extracted_document_url')))
        self.info = info


class InvalidAttachmentPosition(Exception):
    """No attachement found at the given position.
    """
    message = "No attachment found at position {}."

    def __init__(self, position):
        super(InvalidAttachmentPosition, self).__init__(self.message.format(
            position))


class SourceMailNotFound(Exception):
    """Raised when a document extracted from a Mail is modified and its
    info cannot be updated in the Mail from which it was extracted because
    it could not be found"""

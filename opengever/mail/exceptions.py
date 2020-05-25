
class AlreadyExtractedError(Exception):
    """Attachment already extracted from Mail.
    """
    message = "Attachment at position {} has already been extracted to {}."

    def __init__(self, info):
        super(AlreadyExtractedError, self).__init__(self.message.format(
            info.get('position'), info.get('extracted_document_url')))
        self.info = info

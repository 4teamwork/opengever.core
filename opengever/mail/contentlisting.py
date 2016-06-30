from opengever.document.contentlisting import DocumentContentListingObject


class MailContentListingObject(DocumentContentListingObject):

    @property
    def is_document(self):
        return False

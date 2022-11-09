from ftw.upgrade import UpgradeStep
from Products.CMFPlone.utils import safe_unicode


class RemoveNewlinesFromMailDocumentAuthors(UpgradeStep):
    """Remove newlines from mail document authors."""

    deferrable = True

    def __call__(self):
        for mail in self.objects(
            {"object_provides": "opengever.mail.mail.IOGMailMarker"},
            "Remove newlines from mail document authors.",
        ):
            self.remove_newlines(mail)

    def remove_newlines(self, mail):
        author = mail.document_author
        if not author:
            return

        stripped = safe_unicode(author).replace(u"\n", u"").replace(u"\r", u"")
        if stripped == author:
            return

        mail.document_author = stripped
        mail.reindexObject(idxs=["document_author"])

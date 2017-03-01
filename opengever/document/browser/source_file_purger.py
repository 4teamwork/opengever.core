from opengever.document import _
from opengever.document.maintenance import DocumentMaintenance
from plone import api
from Products.Five.browser import BrowserView


class SourceFilePurger(BrowserView):
    """Maintenance view to remove source files of all documents.
    """

    def __call__(self):
        self._dossiers = None

        if self.request.get('purge') == '1':
            return self.purge_files()

        return super(SourceFilePurger, self).__call__()

    def get_expired_dossiers(self):
        if not self._dossiers:
            self._dossiers = DocumentMaintenance().get_dossiers_to_erase()

        return self._dossiers

    def get_documents(self):
        return DocumentMaintenance().get_documents_to_erase_source_file(
            self.get_expired_dossiers())

    def purge_files(self):
        """Remove purge files. XXX
        """
        DocumentMaintenance().purge_source_files()
        msg = _(u'msg_source_files_purged',
                default=u"The source files has been purged successfully.")
        api.portal.show_message(message=msg, request=self.request, type='info')
        return self.request.RESPONSE.redirect(self.context.absolute_url())

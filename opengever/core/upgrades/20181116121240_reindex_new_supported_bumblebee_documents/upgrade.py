from ftw.bumblebee import get_service_v3
from ftw.bumblebee.interfaces import IBumblebeeable
from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.bumblebee.mimetypes import get_extensions_by_mimetype
from ftw.upgrade import UpgradeStep
from ftw.upgrade.progresslogger import ProgressLogger


class ReindexNewSupportedBumblebeeDocuments(UpgradeStep):
    """Reindex new supported bumblebee documents.
    """
    additional_mimetypes = ('indd', 'vsdx', 'vstx', 'vssx')
    deferrable = True

    def __call__(self):
        self.install_upgrade_profile()
        service = get_service_v3()

        msg = 'Reindex checksum for documents having one of the following ' \
              'file-extensions: {}.'.format(', '.join(self.additional_mimetypes))

        for obj in ProgressLogger(msg, self.objs_to_perform()):
            IBumblebeeDocument(obj).update_checksum()
            service.trigger_storing(obj, deferred=True)

    def objs_to_perform(self):
        objs = []
        for brain in self.catalog_unrestricted_search(
                {'object_provides': IBumblebeeable.__identifier__}):

            extension = get_extensions_by_mimetype(brain.getContentType)

            if bool(extension & set(self.additional_mimetypes)):
                objs.append(brain.getObject())

        return objs

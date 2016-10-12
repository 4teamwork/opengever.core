from ftw.bumblebee.browser.download import BumblebeeDownload
from ftw.bumblebee.interfaces import IBumblebeeDocument
from plone import api
from zExceptions import NotFound


class GeverBumblebeeDownload(BumblebeeDownload):

    def find_version_obj_by_checksum(self, obj, checksum):
        """Don't access the document when it is checked out.

        In that case the checksum has not been updated yet and thus is
        equivalent with the checksum of the most recent version.

        """
        if not obj.is_checked_out() and \
                IBumblebeeDocument(obj).get_checksum() == checksum:
            return obj

        repository = api.portal.get_tool('portal_repository')
        for version in repository.getHistory(obj):
            if IBumblebeeDocument(version.object).get_checksum() == checksum:
                return version.object

        raise NotFound('Version not found by checksum.')

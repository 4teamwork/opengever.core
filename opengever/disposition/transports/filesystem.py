from opengever.disposition.interfaces import IDisposition
from opengever.disposition.interfaces import IFilesystemTransportSettings
from opengever.disposition.interfaces import ISIPTransport
from opengever.disposition.transports import BaseTransport
from os.path import abspath
from os.path import expanduser
from os.path import join as pjoin
from plone.registry.interfaces import IRegistry
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
import logging
import os
import shutil
import stat


@implementer(ISIPTransport)
@adapter(IDisposition, IBrowserRequest, logging.Logger)
class FilesystemTransport(BaseTransport):
    """Transport that copies the SIP to a filesystem location specified by
    the IFilesystemTransportSettings.destination_directory registry entry.
    """

    def deliver(self):
        """Delivers the SIP by copying it to the destination_directory.
        """
        destination_dir = self._get_destination_directory()
        assert os.path.isdir(destination_dir)
        sip = self.disposition.get_sip_package()

        blob_path = sip._blob.committed()
        filename = self.disposition.get_sip_filename()
        destination_path = pjoin(destination_dir, filename)

        if os.path.isfile(destination_path):
            self.log.warn("Overwriting existing file %s" % destination_path)

        shutil.copy2(blob_path, destination_path)

        # Make delivered file writable for owner
        st = os.stat(destination_path)
        os.chmod(destination_path, st.st_mode | stat.S_IWUSR)

        self.log.info("Transported %r to %r" % (filename, destination_path))

    def is_enabled(self):
        settings = self._get_settings()
        return settings.enabled

    def _get_destination_directory(self):
        settings = self._get_settings()
        destination_dir = settings.destination_directory
        destination_dir = abspath(expanduser(destination_dir.strip()))
        return destination_dir

    def _get_settings(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IFilesystemTransportSettings)
        return settings

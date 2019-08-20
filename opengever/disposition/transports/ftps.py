from opengever.disposition.interfaces import IDisposition
from opengever.disposition.interfaces import IFTPSTransportSettings
from opengever.disposition.interfaces import ISIPTransport
from opengever.disposition.transports import BaseTransport
from os.path import expanduser
from os.path import join as pjoin
from plone.registry.interfaces import IRegistry
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
import json
import logging
import subprocess


class CurlError(Exception):
    """Raised when cURL returned an exit code other than zero.
    """


class CurlFTPSUploader(object):
    """Helper class to upload files to an FTPS server (with implict TLS).
    """

    def __init__(self, host, port, username, password, max_time=3600, timeout=10, logger=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.common_opts = [
            '-v',                 # verbose, so we get decent logging on STDERR
            '-k',                 # disable SSL certificate validation
            '--ftp-ssl',          # explicitly specify FTPS
            '--disable-epsv',     # Don't attempt EPSV (only needed for IPv6)
            '--connect-timeout',  # connection timeout (seconds)
            str(timeout),
            '--max-time',         # operation timeout (seconds)
            str(max_time),
        ]

        if logger is None:
            logger = logging.getLogger(self.__class__.__name__)
        self.logger = logger

    def list(self):
        """List the directory contents on the FTP server (LIST command)

        This will return a verbose directory listing. This includes additional
        information for ownership, permissions and dates, but is not in a
        standardized format and is not really machine-parseable.
        """
        url = self._build_ftps_url()
        assert url.endswith('/')

        cmd = ['curl'] + self.common_opts + [url]
        (exitcode, stdout, stderr) = self._run_curl_command(cmd)
        return stdout

    def list_only(self):
        """List the directory contents on the FTP server (simple) (NLST command)

        The NLST command only lists names of files, and is therefore much
        better suited for machine parsing. However, some FTP server
        implementations list only files in their response to NLST; they do
        not include sub-directories and symbolic links.
        """
        url = self._build_ftps_url()
        assert url.endswith('/')

        cmd = ['curl', '--list-only'] + self.common_opts + [url]
        (exitcode, stdout, stderr) = self._run_curl_command(cmd)
        return stdout

    def upload(self, src_path, dst_filename):
        """Upload the file from `src_path` to FTP server with dst_filename.
        """
        base_url = self._build_ftps_url()
        upload_url = ''.join((base_url, dst_filename))

        cmd = ['curl', '--upload-file', src_path] + self.common_opts + [upload_url]
        (exitcode, stdout, stderr) = self._run_curl_command(cmd)
        return stdout

    def _build_ftps_url(self):
        url = 'ftps://%s:%s@%s:%s/' % (
            self.username, self.password, self.host, self.port)
        return url

    def _run_curl_command(self, cmd):
        self.logger.info('Running cURL command: %s' % ' '.join(cmd))
        self.logger.info('')

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        for line in stderr.splitlines():
            # Avoid logging plaintext password
            if line.strip().startswith('> PASS'):
                line = 'PASS ******'

            self.logger.info('[stderr] ' + line)
        self.logger.info('')

        for line in stdout.splitlines():
            self.logger.info('[stdout] ' + line)
        self.logger.info('')

        if process.returncode != 0:
            self.logger.error('cURL returned with non-zero exit code %s' % process.returncode)
            self.logger.error("See 'man curl' for a detailed description of exit codes.")
            raise CurlError("Exit code: %s" % process.returncode)

        return (process.returncode, stdout, stderr)


@implementer(ISIPTransport)
@adapter(IDisposition, IBrowserRequest, logging.Logger)
class FTPSTransport(BaseTransport):
    """Transport that uploads the SIP to a FTPS server.
    """

    def deliver(self):
        """Delivers the SIP by uploading it to an FTPS server.
        """
        sip = self.disposition.get_sip_package()
        blob_path = sip._blob.committed()
        filename = self.disposition.get_sip_filename()

        profile = self._get_connection_profile()
        uploader = CurlFTPSUploader(
            host=profile['host'],
            port=profile['port'],
            username=profile['username'],
            password=profile['password'],
            logger=self.log)

        self.log.info('Uploading %s...' % filename)
        uploader.upload(blob_path, filename)

        self.log.info('Checking that uploaded file gets listed...')
        list_result = uploader.list_only()
        assert filename in list_result

        self.log.info('Listing final directory contents (for logs)')
        uploader.list()

        self.log.info('Successfully uploaded %s...' % filename)

    def is_enabled(self):
        settings = self._get_settings()
        return settings.enabled

    def _get_connection_profile(self):
        dotdir = expanduser(pjoin('~', '.opengever'))
        profile_path = pjoin(dotdir, 'ftps_transport', 'profile.json')
        with open(profile_path) as profile_file:
            profile = json.load(profile_file)
        return profile

    def _get_settings(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IFTPSTransportSettings)
        return settings

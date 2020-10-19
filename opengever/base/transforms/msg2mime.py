from distutils import spawn
from opengever.base.sentry import log_msg_to_sentry
from zope.globalrequest import getRequest
import logging
import os
import requests
import shutil
import subprocess
import tempfile


logger = logging.getLogger('opengever.base.transforms')


class Msg2MimeTransform(object):
    """A transform that converts an Outlook .msg file into a RFC822 MIME
    message.
    """

    def transform(self, value):
        msgconvert_url = os.environ.get('MSGCONVERT_URL')
        if msgconvert_url:
            return self.transform_using_service(msgconvert_url, value)
        else:
            return self.transform_using_executable(value)

    def transform_using_service(self, url, value):
        resp = None
        try:
            resp = requests.post(url, files={'msg': value})
            resp.raise_for_status()
        except requests.exceptions.RequestException:
            details = resp.content[:200] if resp is not None else ''
            logger.exception('Msg conversion failed. %s', details)
            raise
        else:
            return resp.content

    def transform_using_executable(self, value):
        # Create a temporary directory for 'msgconvert' to work in. It dumps
        # the resulting .eml file to its working directory, and doesn't take
        # an commandline option to actually specify the output path, so we
        # have it do its work in a tempdir and predict the output filename.
        tempdir = tempfile.mkdtemp()

        # Create a temporary msg file in the tempdir we just created
        msg_path = os.path.join(tempdir, 'mail.msg')
        with open(msg_path, 'wb') as msg_file:
            msg_file.write(value)

        msgconvert_path = spawn.find_executable("msgconvert")
        if msgconvert_path is None:
            error = 'msgconvert not found in $PATH'
            log_msg_to_sentry(
                error,
                request=getRequest())
            raise EnvironmentError(error)

        process = subprocess.Popen(
            [msgconvert_path, msg_path],
            bufsize=0,
            cwd=tempdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True)

        # Wait for subprocess to terminate.
        stdout, stderr = process.communicate()

        # The converted .eml file will be placed in the working directory
        eml_path = os.path.join(tempdir, 'mail.eml')
        with open(eml_path) as eml_file:
            eml_data = eml_file.read()

        # Remove temp directory
        shutil.rmtree(tempdir)

        # If program terminated correctly return converted message
        if process.returncode == 0:
            return eml_data
        # If program terminated with error, raise exception
        else:
            msg = 'Program terminated with error code %s\n%s' % (
                process.returncode, stderr)
            raise IOError(msg)

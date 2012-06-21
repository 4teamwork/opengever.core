import opengever.base
import os
import subprocess
import tempfile


class Msg2MimeTransform(object):
    """A transform that converts an Outlook .msg file into a RFC822 MIME
       message.
    """

    def __call__(self, value):
        # Create a temporary msg file.
        msg_file = tempfile.NamedTemporaryFile(delete=False)
        msg_file.write(value)
        msg_file.close()

        # Locate conversion tool and launch it as a subprocess.
        cmd = os.path.join(
            os.path.dirname(opengever.base.__file__),
            'transforms',
            'msg2mime.pl')

        process = subprocess.Popen([cmd, msg_file.name], bufsize=0,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)

        # Wait for subprocess to terminate.
        stdout, stderr = process.communicate()

        # Remove temporary msg file.
        os.unlink(msg_file.name)

        # If program terminated correctly return converted message
        if process.returncode == 0:
            return stdout
        # If program terminated with error, raise exception
        else:
            raise IOError(), 'Program terminated with error code %s\n%s' % (
                process.returncode, stderr)

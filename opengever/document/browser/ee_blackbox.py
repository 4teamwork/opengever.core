from datetime import datetime
from five import grok
from opengever.document.document import IDocumentSchema
import logging
import os


logger = logging.getLogger('opengever.document')


class ExternalEditorBlackboxUploadView(grok.View):
    """ This view accepts a blackbox file (ZIP of EE related debugging info) via POST
    request and saves it to the var directory of the current buildout.
    """
    grok.context(IDocumentSchema)
    grok.name('ee-blackbox-upload')
    #grok.require('zope2.Public')

    def render(self):
        # Set correct content type for response
        self.request.response.setHeader("Content-type", "text/plain")

        ee_session_status = self.request.form.get('status', 'UNKNOWN')
        file_upload = self.request.form.get('upload')
        if not file_upload:
            return "FAILED: No file uploaded"
        file_data = file_upload.read()

        blackbox_dir = os.environ.get('BLACKBOX_DIR', 'var/blackbox')
        if not os.path.isdir(blackbox_dir):
            os.mkdir(blackbox_dir)

        timestamp = datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
        filename = "blackbox-%s.zip" % timestamp
        path = os.path.join(blackbox_dir, filename)
        outfile = open(path, 'w')
        outfile.write(file_data)
        outfile.close()
        logger.info("Blackbox from EE session (status: %s) saved to %s" % (ee_session_status, path))

        return 'OK'

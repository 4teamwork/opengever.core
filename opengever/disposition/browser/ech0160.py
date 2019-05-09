from opengever.base.stream import TempfileStreamIterator
from opengever.disposition import _
from opengever.disposition.ech0160.sippackage import SIPPackage
from plone import api
from plone.namedfile.utils import set_headers
from plone.namedfile.utils import stream_data
from Products.Five import BrowserView
from pyxb.utils.domutils import BindingDOMSupport
from tempfile import TemporaryFile
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile


class ECH0160ExportView(BrowserView):
    """A view which creates an eCH-0160 export of all dossiers
    form the disposition.
    """

    def __call__(self):
        BindingDOMSupport.SetDefaultNamespace(u'http://bar.admin.ch/arelda/v4')

        package = SIPPackage(self.context)
        tmpfile = self.create_zipfile(package)

        size = tmpfile.tell()
        response = self.request.response
        response.setHeader(
            "Content-Disposition",
            'inline; filename="%s.zip"' % package.get_folder_name())
        response.setHeader("Content-type", "application/zip")
        response.setHeader("Content-Length", size)

        return TempfileStreamIterator(tmpfile, size)

    def create_zipfile(self, package):
        tmpfile = TemporaryFile()
        with ZipFile(tmpfile, 'w', ZIP_DEFLATED, True) as zipfile:
            package.write_to_zipfile(zipfile)

        return tmpfile


class ECH0160StoreView(BrowserView):
    """A view which generates and store's the SIP package as a blob file.
    """

    def __call__(self):
        self.context.store_sip_package()
        msg = _('msg_sip_package_sucessfully_generated',
                default=u'SIP Package generated successfully.')
        api.portal.show_message(msg, request=self.request, type='info')
        return self.request.RESPONSE.redirect(self.context.absolute_url())


class ECH0160DownloadView(BrowserView):
    """View which streams the existing SIP Package. Redirect and show status
    message when SIP package does not exist.
    """

    def __call__(self):
        if not self.context.has_sip_package():
            msg = _('msg_no_sip_package_generated',
                    default=u'No SIP Package generated for this disposition')
            api.portal.show_message(msg, request=self.request, type='error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        sip_package = self.context.get_sip_package()
        set_headers(sip_package, self.request.response,
                    u'{}.zip'.format(self.context.get_sip_name()))
        return stream_data(sip_package)

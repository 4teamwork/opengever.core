from opengever.base.stream import TempfileStreamIterator
from opengever.disposition.ech0160.sippackage import SIPPackage
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

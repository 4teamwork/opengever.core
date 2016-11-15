from opengever.base.stream import TempfileStreamIterator
from opengever.disposition.ech0160.sippackage import SIPPackage
from plone import api
from Products.Five import BrowserView
from pyxb.utils.domutils import BindingDOMSupport
from tempfile import TemporaryFile
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile


class ECH0160ExportView(BrowserView):
    """A view which create export
    WIP: only export selected or refrenced dossiers instead of all dosiers.
    """

    def __call__(self):
        BindingDOMSupport.SetDefaultNamespace(u'http://bar.admin.ch/arelda/v4')

        package = SIPPackage(self.get_dossiers())
        tmpfile = self.create_zipfile(package)

        size = tmpfile.tell()
        response = self.request.response
        response.setHeader(
            "Content-Disposition",
            'inline; filename="%s.zip"' % package.get_folder_name())
        response.setHeader("Content-type", "application/zip")
        response.setHeader("Content-Length", size)

        return TempfileStreamIterator(tmpfile, size)

    def get_dossiers(self):
        brains = api.portal.get_tool('portal_catalog')(
            portal_type='opengever.dossier.businesscasedossier')
        return [brain.getObject() for brain in brains]

    def create_zipfile(self, package):
        tmpfile = TemporaryFile()
        with ZipFile(tmpfile, 'w', ZIP_DEFLATED, True) as zipfile:
            package.write_to_zipfile(zipfile)

        return tmpfile

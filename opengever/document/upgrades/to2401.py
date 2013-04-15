from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
import os


class NormalizeFileTitles(UpgradeStep):
    """Normalize all Filenames"""

    def __call__(self):
        catalog = self.getToolByName('portal_catalog')
        brains = catalog.unrestrictedSearchResults(
            portal_type='opengever.document.document')

        id_normalizer = getUtility(IIDNormalizer)

        with ProgressLogger('Normalize filenames', brains) as step:
            for brain in brains:
                doc = brain.getObject()
                if doc.file:
                    basename, ext = os.path.splitext(doc.file.filename)
                    if basename != id_normalizer.normalize(doc.title):
                        doc.file.filename = ''.join(
                            [id_normalizer.normalize(doc.title), ext])
                step()

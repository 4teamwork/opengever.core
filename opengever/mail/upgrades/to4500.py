from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from ZODB.POSException import ConflictError
import logging


logger = logging.getLogger('ftw.upgrade')


class UpgradeMailMessageFilename(UpgradeStep):

    def __call__(self):
        objects = self.catalog_unrestricted_search(
            {'portal_type': 'ftw.mail.mail'}, full_objects=True)

        for mail in ProgressLogger('Migrate mail message filename', objects):
            try:
                mail.update_filename()
            except ConflictError:
                raise
            except Exception, e:
                logger.warn("Updating object {0} failed: {1}".format(
                    mail.absolute_url(), str(e)))

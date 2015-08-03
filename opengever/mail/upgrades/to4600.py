from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep


class InitializeFtwMailCaches(UpgradeStep):

    def __call__(self):
        objects = self.catalog_unrestricted_search(
            {'portal_type': 'ftw.mail.mail'}, full_objects=True)

        for mail in ProgressLogger('Initialize ftw.mail caches', objects):
            # initialize attributes (lazy attribute loading)
            mail.Title()

            # initialize cached data
            mail._message = vars(mail).get('message')
            mail._update_attachment_infos()
            mail._reset_header_cache()

            # preserve title, move from 'title' to '_title'
            mail.title = vars(mail).get('title')

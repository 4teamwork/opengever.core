from ftw.upgrade import UpgradeStep
from opengever.base.response import IResponseContainer
from opengever.disposition.response import DispositionResponse
from zope.annotation import IAnnotations


class MigrateDispositionHistory(UpgradeStep):
    """Migrate disposition history.
    """

    deferrable = True

    old_key = 'disposition_history'

    def __call__(self):
        self.install_upgrade_profile()

        for disposition in self.objects(
                {'portal_type': 'opengever.disposition.disposition'},
                'Migrate disposition history'):

            self.migrate_history(disposition)

    def migrate_history(self, disposition):
        ann = IAnnotations(disposition)
        if self.old_key not in ann.keys():
            return

        container = IResponseContainer(disposition)

        for item in ann.get(self.old_key):
            response = DispositionResponse(response_type=item.get('transition'))
            response.created = item.get('date')
            response.creator = item.get('actor_id')
            response.dossiers = item.get('dossiers')
            container.add(response)

        ann.pop(self.old_key)

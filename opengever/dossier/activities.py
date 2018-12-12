from opengever.activity.base import BaseActivity
from opengever.activity.roles import DOSSIER_RESPONSIBLE_ROLE
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossier


class DossierOverdueActivity(BaseActivity):
    """Activity representation for an overdue dossier"""

    kind = 'dossier-overdue'
    system_activity = True

    @property
    def label(self):
        return self.translate_to_all_languages(
            _('label_dossier_overdue_activity', u'Overdue dossier'))

    @property
    def summary(self):
        msg = _('summary_dossier_overdue_activity',
                u'The dossier is still open after exceeding its end date.')
        return self.translate_to_all_languages(msg)

    @property
    def description(self):
        return {}

    def before_recording(self):
        """The responsible of an overdue dossier will be notified. To be in
        sync with the current responsible user, we have two options:

        1. we could listen to an object-modified event and update the responsible
        watcher on every edition for every dossier or
        2. we update the watcher on activity creation only for the overdue
        dossiers.

        Because it is much more performant and much easier to update the watcher
        on activity creation, we update the current watcher with the responsible
        role before recoriding the overdue activity.

        Warning: This implementation does not allow using the
        DOSSIER_RESPONSIBLE_ROLE for other activities because we do not
        update the the responsible on dossier-edition. But setting a watcher
        for every dossier on every dossier-edition is currently not desired and
        not necessary. That's why we implemented the second option.
        """
        self.center.remove_watchers_from_resource_by_role(
            self.context, DOSSIER_RESPONSIBLE_ROLE)

        self.center.add_watcher_to_resource(
            self.context, IDossier(self.context).responsible,
            DOSSIER_RESPONSIBLE_ROLE)

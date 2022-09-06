from ftw.bumblebee.interfaces import IBumblebeeable
from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import FixGhostChecksums


class UpdateBumblebeeGhostChecksums(UpgradeStep):
    """Update bumblebee ghost checksums.
    """

    def __call__(self):
        with FixGhostChecksums() as ghost_checksum_fixer:
            query = {'object_provides': IBumblebeeable.__identifier__}
            for brain in self.brains(query, 'Fix ghost checksums of non convertable documents'):
                ghost_checksum_fixer.add_by_brain(brain)

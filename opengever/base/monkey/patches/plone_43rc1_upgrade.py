from opengever.base.monkey.patching import MonkeyPatch


def nullupgrade(context):
    pass


class PatchPlone43RC1Upgrade(MonkeyPatch):
    """Marmoset patch `plone.app.upgrade.v43.betas.to43rc1` to delay an
    expensive upgrade.

    The upgrade is re-defined as opengever.policy.base.to4504.
    """

    def __call__(self):
        from opengever.base.marmoset_patch import marmoset_patch

        from plone.app.upgrade.v43 import betas
        marmoset_patch(betas.to43rc1, nullupgrade)

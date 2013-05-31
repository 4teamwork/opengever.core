from plone.app.upgrade.utils import loadMigrationProfile


def to_v2201(context):
    """Upgrade profile v2201
    """
    loadMigrationProfile(context, 'profile-opengever.advancedsearch.upgrades:to_v2201')
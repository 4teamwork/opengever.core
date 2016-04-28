from opengever.base.monkey.patching import MonkeyPatch


class PatchWebDAVLockTimeout(MonkeyPatch):
    """Increase WebDAV lock timeout to 24h by monkey patching.

    This is intended to reduce the amount of PreconditionFailed errors with
    Zope External Editor in cases where people keep documents open for long
    periods of time.
    """

    def __call__(self):
        new_timeout = 24 * 60 * 60L   # 24h

        from webdav import LockItem
        self.patch_value(LockItem, 'DEFAULTTIMEOUT', new_timeout)

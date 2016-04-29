from opengever.base.monkey.patching import MonkeyPatch


class PatchZ2LogTimezone(MonkeyPatch):
    """Patch the computed timezone for Z2 logs in order to fix a DST bug.
    """

    def __call__(self):

        import time

        def compute_tz():
            """Patched version of http_server's compute_timezone_for_log
            that correctly determines whether daylight saving time currently
            is in effect or not.
            """
            def is_dst():
                return time.localtime().tm_isdst

            if is_dst():
                tz = time.altzone
            else:
                tz = time.timezone
            if tz > 0:
                neg = 1
            else:
                neg = 0
                tz = -tz
            h, rem = divmod (tz, 3600)
            m, rem = divmod (rem, 60)

            if neg:
                return '-%02d%02d' % (h, m)
            else:
                return '+%02d%02d' % (h, m)

        from ZServer.medusa import http_server
        self.patch_refs(http_server, 'compute_timezone_for_log', compute_tz)
        self.patch_value(http_server, 'tz_for_log', compute_tz())

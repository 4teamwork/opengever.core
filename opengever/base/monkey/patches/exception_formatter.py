from opengever.base.monkey.patching import MonkeyPatch


class PatchExceptionFormatter(MonkeyPatch):
    """Return an empty user-facing traceback for non-manager users.

    This is done as ``Unauthorized`` is explicitly rerisen for PAS plugins and
    this ends up bypassing the ``opengever.base`` exception template and
    falling back to normal exception rendering mechanisms.
    """

    def __call__(self):
        from App.config import getConfiguration
        from plone import api
        from ZODB.DemoStorage import DemoStorage

        def formatException(self, etype, value, tb, limit=None):
            portal = api.portal.get()
            user_is_manager = api.user.has_permission("Manage Portal", obj=portal)
            in_a_test = isinstance(portal._p_jar.db().storage, DemoStorage)

            config = getConfiguration()
            debug_mode = getattr(config, "debug_mode", False)
            verbose_security = getattr(config, "verbose_security", False)

            # The block within this if is the original implementation
            # https://github.com/zopefoundation/zExceptions/blob/85343157fa49f04b5304f8394d27400804b292df/src/zExceptions/ExceptionFormatter.py#L178-L199
            if user_is_manager or in_a_test or debug_mode or verbose_security:
                # The next line provides a way to detect recursion.
                __exception_formatter__ = 1
                result = [self.getPrefix() + "\n"]
                if limit is None:
                    limit = self.getLimit()
                n = 0
                while tb is not None and (limit is None or n < limit):
                    if tb.tb_frame.f_locals.get("__exception_formatter__"):
                        # Stop recursion.
                        result.append("(Recursive formatException() stopped)\n")
                        break
                    line = self.formatLine(tb)
                    result.append(line + "\n")
                    tb = tb.tb_next
                    n = n + 1
                exc_line = self.formatExceptionOnly(etype, value)
                result.append(self.formatLastLine(exc_line))
                return result

            # We fall through in our patch with a notification of a suppression
            return ["Exception suppressed."]

        from zExceptions.ExceptionFormatter import HTMLExceptionFormatter
        self.patch_refs(HTMLExceptionFormatter, "formatException", formatException)

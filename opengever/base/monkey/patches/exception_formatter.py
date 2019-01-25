from opengever.base.monkey.patching import MonkeyPatch


class PatchExceptionFormatter(MonkeyPatch):
    """Return an empty user-facing traceback for non-manager users.

    This is done as ``Unauthorized`` is explicitly rerisen for PAS plugins and
    this ends up bypassing the ``opengever.base`` exception template and
    falling back to normal exception rendering mechanisms.
    """

    def __call__(self):
        from plone import api

        def formatException(self, etype, value, tb, limit=None):
            # The block within this if is the original implementation
            if api.user.has_permission("Manage Portal", obj=api.portal.get()):
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

        from zExceptions.ExceptionFormatter import TextExceptionFormatter
        self.patch_refs(TextExceptionFormatter, "formatException", formatException)

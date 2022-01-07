from opengever.base.monkey.patching import MonkeyPatch


class PatchMaybeReportException(MonkeyPatch):
    """Monkeypatch for ftw.raven.reporter.maybe_report_exception

    This allows to skip reporting of exceptions that inherit NotReportedException
    """

    def __call__(self):
        from opengever.base.sentry import FTW_RAVEN_AVAILABLE
        if not FTW_RAVEN_AVAILABLE:
            return

        from ftw.raven.reporter import maybe_report_exception as original_maybe_report_exception
        from opengever.api.not_reported_exceptions import NotReportedException

        def maybe_report_exception(context, request, exc_type, exc, traceback):
            if isinstance(exc, NotReportedException):
                return
            return original_maybe_report_exception(context, request, exc_type, exc, traceback)

        from ftw.raven import reporter
        self.patch_refs(reporter, 'maybe_report_exception', maybe_report_exception)

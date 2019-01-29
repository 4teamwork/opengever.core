from opengever.base.monkey.patching import MonkeyPatch


class ScrubBoboExceptions(MonkeyPatch):
    """We do not use the Bobo exception headers for anything."""

    def __call__(self):
        def _setBCIHeaders(self, t, tb):
            # Original implementation:
            # https://github.com/zopefoundation/Zope/blob/d916c812bdaf518053b0c3cb2cb3545ff73bc288/src/ZPublisher/HTTPResponse.py#L758-L787
            del tb
        from ZPublisher.HTTPResponse import HTTPResponse
        self.patch_refs(HTTPResponse, "_setBCIHeaders", _setBCIHeaders)

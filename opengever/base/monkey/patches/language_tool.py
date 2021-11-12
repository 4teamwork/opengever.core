from opengever.base.monkey.patching import MonkeyPatch
from Products.PloneLanguageTool.LanguageTool import LanguageTool
from ZPublisher.HTTPRequest import HTTPRequest


class PatchLanguageToolCall(MonkeyPatch):
    """"Patch LangugageTool to make sure the setLanguageBindings is also done
    for PATCH requests
    """

    def __call__(self):

        def __new__call__(self, container, req):
            if req.other.has_key('LANGUAGE_TOOL'):
                return None
            if req.__class__ is not HTTPRequest:
                return None

            # patch: add PATCH to requests methods
            if not req['REQUEST_METHOD'] in ('HEAD', 'GET', 'PUT', 'POST', 'PATCH'):
                return None
            if req.environ.has_key('WEBDAV_SOURCE_PORT'):
                return None
            # Bind the languages
            self.setLanguageBindings()

        locals()['__patch_refs__'] = False
        original_call = LanguageTool.__call__

        self.patch_refs(LanguageTool, '__call__', __new__call__)

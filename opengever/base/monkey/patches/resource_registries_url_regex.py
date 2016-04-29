from opengever.base.monkey.patching import MonkeyPatch


class PatchResourceRegistriesURLRegex(MonkeyPatch):
    """Monkey patch the regex used to replace relative paths in url()
    statements with absolute paths in the portal_css tool.

    This has been fixed as of release 3.0.3 of Products.ResourceRegistries
    which is only available for Plone 5.
    See https://github.com/plone/Products.ResourceRegistries/commit/4f909491
    """

    def __call__(self):
        import re

        new_regex = re.compile(
            r'''(url\s*\(\s*['"]?)(?!data:)'''
            r'''([^'")]+)(['"]?\s*\))''', re.I | re.S)

        from Products.ResourceRegistries import utils
        self.patch_value(utils, 'URL_MATCH', new_regex)

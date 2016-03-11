from opengever.base.pathfinder import PathFinder
from opengever.base.schemadump.config import SCHEMA_DOCS_DIR
from opengever.base.schemadump.config import SCHEMA_DUMPS_DIR
from os.path import join as pjoin
from zope.i18n import translate


class DirectoryHelperMixin(object):

    def __init__(self, buildout_dir=None):
        self.buildout_dir = buildout_dir

        if buildout_dir is None:
            self.buildout_dir = PathFinder().buildout

    @property
    def schema_dumps_dir(self):
        return pjoin(self.buildout_dir, SCHEMA_DUMPS_DIR)

    @property
    def schema_docs_dir(self):
        return pjoin(self.buildout_dir, SCHEMA_DOCS_DIR)


def join_lines(lines):
    return u'\n'.join(lines)


def translate_de(*args, **kwargs):
    kwargs.update({'target_language': 'de'})
    return translate(*args, **kwargs)

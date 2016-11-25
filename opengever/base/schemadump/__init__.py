from opengever.base.schemadump.schema import dump_oggbundle_schemas
from opengever.base.schemadump.schema import dump_schemas
from opengever.core.debughelpers import get_first_plone_site
from opengever.core.debughelpers import setup_plone


def dump_schemas_zopectl_handler(app, args):
    """Handler for the 'bin/instance dump_schemas' zopectl command.
    """
    setup_plone(get_first_plone_site(app))
    dump_schemas()
    dump_oggbundle_schemas()

from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import resolvePackageReferenceOrFile
from opengever.ogds.base.utils import get_current_org_unit
from zope.interface import classProvides, implements
import json


class JSONRolesSourceSection(object):
    """Loads roles configuration from a json source file, substituting
    some client config attribtues.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        org_unit = get_current_org_unit()

        replace_map = {
            'users_group': org_unit.users_group.groupid,
            'inbox_group': org_unit.inbox_group.groupid,
            'client_id': org_unit.id(),
            }

        repository_root = transmogrifier.context.REQUEST.get(
            'repository_root', None)
        if repository_root:
            replace_map['repository_root_name'] = repository_root[0]

        filename = resolvePackageReferenceOrFile(options['filename'])
        file_ = open(filename, 'r')
        data = file_.read() % replace_map

        self.source = json.loads(data)

    def __iter__(self):
        for item in self.previous:
            yield item

        for item in self.source:
            yield item

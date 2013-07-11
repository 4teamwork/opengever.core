from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from collective.transmogrifier.utils import resolvePackageReferenceOrFile
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import getUtility
from zope.event import notify
from zope.interface import classProvides, implements
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema import getFields


class NamedFileCreatorSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.field = options.get('field')
        self.key = options.get('key')
        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')
        self.typekey = defaultMatcher(options, 'type-key', name, 'type',
                                      ('portal_type', 'Type'))

    def __iter__(self):
        for item in self.previous:
            filename = resolvePackageReferenceOrFile(item[self.key])
            file_ = open(filename, 'r')

            keys = item.keys()
            pathkey = self.pathkey(*keys)[0]
            typekey = self.typekey(*keys)[0]

            # Get the file object by path
            path = item[pathkey]
            obj = self.context.unrestrictedTraverse(path.lstrip('/'), None)
            if obj is None:         # path doesn't exist
                yield item
                continue

            if not file_:
                yield item
                continue

            # Set file field
            fti = getUtility(IDexterityFTI, name=item[typekey])
            schema = fti.lookupSchema()
            field = getFields(schema)[self.field]

            # Don't pass the file descriptor but only the file's data as
            # a string, because else the source files get removed!
            filedata = file_.read()
            filename = file_.name[file_.name.rfind('/') + 1:].decode('utf-8')
            fileobj = field._type(filedata, filename=filename)

            field.set(field.interface(obj), fileobj)

            # Fire ObjectModifiedEvent so that digitally_available gets set
            notify(ObjectModifiedEvent(obj))
            yield item

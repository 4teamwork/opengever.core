from zope.interface import classProvides, implements
from zope.component import getUtility
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from zope.schema import getFields
from plone.dexterity.interfaces import IDexterityFTI
from collective.transmogrifier.utils import resolvePackageReferenceOrFile
from collective.transmogrifier.utils import defaultMatcher

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
                yield item; continue
            
            if not file_:
                yield item; continue
            
            # Set file field
            fti = getUtility(IDexterityFTI, name=item[typekey])
            schema = fti.lookupSchema()
            field = getFields(schema)[self.field]
            fileobj = field._type(file_, filename=file_.name[file_.name.rfind('/')+1:].decode('utf-8'))
            field.set(field.interface(obj), fileobj)
            yield item
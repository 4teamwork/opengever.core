import json
from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection

from collective.transmogrifier.utils import resolvePackageReferenceOrFile

class JSONSourceSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)
    
    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        
        filename = resolvePackageReferenceOrFile(options['filename'])
        file_ = open(filename, 'r')

        self.source = json.loads(file_.read())
    
    def __iter__(self):
        for item in self.previous:
            yield item
        
        for item in self.source:
            yield item

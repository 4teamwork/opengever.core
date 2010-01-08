import csv

from z3c.form.interfaces import IValue, IFieldWidget
from zope.component import getUtility, queryUtility, queryMultiAdapter
from zope.component import createObject
from zope.schema import getFieldsInOrder

from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity import utils
from plone.namedfile.interfaces import INamedFileField

tolist = lambda f:lambda *a,**k:list(f(*a,**k))

DIRECT_ATTRIBUTES = (
    'title',
    'Title',
    'effective_title',
    )

class GenericContentCreator(object):

    def __init__(self, setup, fileencoding='iso-8859-1'):
        self.setup = setup
        self.portal = self.setup.getSite()
        self.openDataFile = self.setup.openDataFile
        self.fileencoding = fileencoding

    @tolist
    def create_from_csv(self, filename, checkConstraints=True):
        stream = self.openDataFile(filename)
        portal_type = stream.readline().strip()
        data_rows = self._get_objects_data(stream)
        print '* IMPORT %s FROM %s' % (len(data_rows), filename)
        for data in data_rows:
            pathish_title = data.get(self.fieldnames[0])
            data[self.fieldnames[0]] = pathish_title.split('/')[-1].strip()
            obj = self.get_object_by_pathish_title(pathish_title)
            if obj:
                continue
            if len(pathish_title.split('/')) == 1:
                container = self.portal
            else:
                container_title = '/'.join(pathish_title.split('/')[:-1])
                container = self.get_object_by_pathish_title(container_title)
                if not container:
                    print 'Could not find object', container_title
            # create the object
            obj = self._create_object(container, portal_type,
                                      checkConstraints=checkConstraints, **data)
            print '** created', obj
            yield obj

    def get_object_by_pathish_title(self, title, container=None):
        if not container:
            container = self.portal
        parts = title.split('/')
        next_title = parts[0].strip()
        for id in container.objectIds():
            obj = container.get(id)
            title = getattr(obj, self.fieldnames[0],
                            getattr(obj, 'title',
                                    getattr(obj, 'Title', None)))
            if not title:
                continue
            if isinstance(title, str) or isinstance(title, unicode):
                title = title.strip()
            if title==next_title:
                if len(parts)==1:
                    return obj
                else:
                    return self.get_object_by_pathish_title('/'.join(parts[1:]),
                                                            obj)
        return None

    def _get_objects_data(self, csv_stream):
        pos = csv_stream.tell()
        dialect = csv.Sniffer().sniff(csv_stream.read(1024))
        csv_stream.seek(pos)
        reader = csv.DictReader(csv_stream, dialect=dialect)
        rows = list(reader)
        self.fieldnames = reader.fieldnames
        # we need to convert the values to unicode
        for row in rows:
            for key, value in row.items():
                if isinstance(value, str):
                    row[key] = unicode(value.decode(self.fileencoding))
        if len(rows)>0 and rows[0].has_key(''):
            for row in rows:
                if row.has_key(''):
                    row.pop('')
        return rows

    def _get_all_fields_of(self, obj):
        fields = {}
        for schemata in utils.iterSchemata(obj):
            for name, field in getFieldsInOrder(schemata):
                fields[name] = field
        return fields

    def _create_object(self, container, type, checkConstraints=True, **kw):
        fti = queryUtility(IDexterityFTI, name=type)
        if fti:
            filtered_kw = dict(filter(lambda a:a[0] in DIRECT_ATTRIBUTES,
                                      kw.items()))
            # Dexterity
            obj = utils.createContentInContainer(container, type,
                                                 checkConstraints=checkConstraints,
                                                 **filtered_kw)
            self._update_dexterity_object(obj, **kw)
            obj.reindexObject()
            return obj
        else:
            # Archetypes
            obj = createObject(type)
            for key, value in kw.items():
                setattr(obj, key, value)
            utils.addContentToContainer(container, obj, checkConstraints=False)
            obj.reindexObject()
            return obj

    def _update_dexterity_object(self, obj, **kw):
        fields = {}
        for schemata in utils.iterSchemata(obj):
            for name, field in getFieldsInOrder(schemata):
                fields[name] = field
        for k, v in kw.items():
            field = fields[k]
            if k in fields.keys():
                if v.lower()=='true':
                    v = True
                elif v.lower()=='false':
                    v = False
                if INamedFileField.providedBy(field) and v:
                    source = self.openDataFile(v.strip())
                    if source:
                        filename = v.strip().split('/')[-1]
                        file_ = field._type(data=source.read(), filename=filename)
                        field.set(field.interface(obj), file_)
                        continue
                field.set(field.interface(obj), v)
            else:
                print '*** WARNING: field %s not found for object' % k, obj
        for name, field in fields.items():
            if name not in kw.keys():
                # get default value
                default = queryMultiAdapter((
                        obj,
                        obj.REQUEST, # request
                        None, # form
                        field,
                        None, # Widget
                        ), IValue, name='default')
                if default!=None:
                    default = default.get()
                if default==None:
                    default = getattr(field, 'default', None)
                if default==None:
                    try:
                        # dispairing attempt to get a valid value....
                        default = field._type()
                    except:
                        pass
                if default==None:
                    print '     could not find default for field', name, field
                field.set(field.interface(obj), default)

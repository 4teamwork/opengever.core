import csv

from z3c.form.interfaces import IValue, IFieldWidget
from zope.component import getUtility, queryUtility, queryMultiAdapter
from zope.component import createObject
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IList

from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity import utils
from plone.namedfile.interfaces import INamedFileField

tolist = lambda f:lambda *a,**k:list(f(*a,**k))

DIRECT_ATTRIBUTES = (
    # Direct attributes are passed to createContentInContainer and used to instate the
    # object. For keywords like title and id, but should not be used for normal behavior
    # fields, since they may not bestored at the object itself but on a persistent adapter
    # of the object
    'title',
    'Title',
    'effective_title',
    'firstname',
    'lastname',
    'id',
    )
META_ATTRIBUTES = (
    # Thes attributes are not field-values and are not set within the
    # _update_dexterity_object method (which fails if the field does not exist).
    'location',
    'id',
    )

def aggressive_decode(value, encoding='utf-8'):
    if isinstance(value, unicode):
        return value
    other_encodings = filter(lambda e:e is not encoding, [
            'utf8',
            'iso-8859-1',
            'latin1',
            ])
    encodings = [encoding] + other_encodings
    if not isinstance(value, str):
        value = str(value)
    for enc in encodings:
        try:
            return value.decode(enc)
        except UnicodeDecodeError:
            pass
    raise


class GenericContentCreator(object):
    """
    Column name postfixes:

    field:unique : field should be unique per container
    """

    def __init__(self, setup, fileencoding='utf-8'):
        self.setup = setup
        self.portal = self.setup.getSite()
        self.openDataFile = self.setup.openDataFile
        self.fileencoding = fileencoding

    @tolist
    def create_from_csv(self, filename, checkConstraints=True):
        stream = self.openDataFile(filename)
        portal_type = stream.readline().replace(';','').replace('"','') \
            .replace(',','').strip()
        data_rows = self._get_objects_data(stream)
        print '* IMPORT %s FROM %s' % (len(data_rows), filename)
        for ori_data in data_rows:
            use_location = self.fieldnames[0]=='location'
            data = {}
            for key, value in ori_data.items():
                key = key.split(':')[0].strip()
                data[key] = value
            pathish_title = data.get(self.fieldnames[0])
            data[self.fieldnames[0]] = pathish_title.split('/')[-1].strip()
            obj = self.get_object_by_pathish_title(pathish_title)
            if obj and not use_location:
                continue
            elif obj and use_location:
                container = obj
                obj = None
            elif len(pathish_title.split('/')) == 1:
                container = self.portal
            else:
                container_title = '/'.join(pathish_title.split('/')[:-1])
                container = self.get_object_by_pathish_title(container_title)
                if not container:
                    print 'Could not find object', container_title
                    continue
            # create the object
            if not self._find_object(container, portal_type, **ori_data):
                obj = self._create_object(container, portal_type,
                                          checkConstraints=checkConstraints, **data)
                print '** created', obj
                yield obj

    def _find_object(self, container, portal_type, **ori_data):
        childs_of_same_type = [container.get(id) for id in container.objectIds()
                               if container.get(id).portal_type==portal_type]
        unique_data = dict([(k.split(':')[0].strip() ,v)
                            for k, v in ori_data.items()
                            if k.endswith(':unique')])
        for obj in childs_of_same_type:
            fields = self._get_all_fields_of(obj)
            for key, value in unique_data.items():
                try:
                    field = fields[key]
                except AttributeError:
                    continue
                repr = field.interface(obj)
                if field.get(repr) == value:
                    return obj
        return None

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
                    row[key] = aggressive_decode(value, self.fileencoding)
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
            if k in META_ATTRIBUTES:
                continue
            if k in fields.keys():
                field = fields[k]
                if v.lower()=='true':
                    v = True
                elif v.lower()=='false':
                    v = False
                try:
                    v = int(v)
                except ValueError:
                    pass
                if IList.providedBy(field):
                    v = filter(lambda p:not not p,
                               [p.strip() for p in v.split(',')])
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

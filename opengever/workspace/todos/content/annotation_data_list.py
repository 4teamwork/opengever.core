from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone.restapi.serializer.converters import json_compatible
from zope.annotation import IAnnotations
from zope.interface import providedBy
from zope.schema._bootstrapinterfaces import RequiredMissing


_missing = object()


class ItemWrapperBase(object):

    def __init__(self, **kwargs):
        self._data = PersistentMapping(kwargs)
        self.validate()

    def __setattr__(self, name, value):
        if name == '_data':
            self.__dict__.update({name: value})
        else:
            self._data.update({name: value})

    def __getattr__(self, name):
        if name not in self._data:
            raise AttributeError(name)
        return self._data.get(name)

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        return self.id == other.id

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.validate()
        return self

    @classmethod
    def from_mapping(kls, data):
        self = kls.__new__(kls)
        self._data = data
        return self

    def as_json_compatible(self):
        keys, values = zip(*self._data.items())
        values = map(json_compatible, values)
        return dict(zip(keys, values))

    def validate(self):
        for schema in providedBy(self):
            for name in schema.names():
                self.validate_field(name, schema.get(name))

    def validate_field(self, name, field):
        value = getattr(self, name, _missing)
        if field.required and value is _missing:
            raise RequiredMissing(name)
        field.bind(self).validate(value)


class AnnotationDataListBase(object):

    annotations_key = None
    item_class = None
    writeable_attributes = None

    def __init__(self, context):
        if self.annotations_key is None:
            raise ValueError('annotations_key must be defined.')
        if self.item_class is None:
            raise ValueError('item_class must be defined.')
        if self.writeable_attributes is None:
            raise ValueError('writeable_attributes must be defined.')

        self.context = context
        self.annotations = IAnnotations(context)
        self.auto_increment_annotations_key = (
            self.annotations_key + ':auto_increment')

    def all(self):
        return tuple(map(self.item_class.from_mapping,
                         self.annotations.get(self.annotations_key, ())))

    def get(self, item_id):
        for item in self.all():
            if item.id == item_id:
                return item

        raise KeyError('Item with id {!r} not found.'.format(item_id))

    def create(self, **kwargs):
        return self.append(self.item_class(**kwargs))

    def append(self, item):
        if not isinstance(item, self.item_class):
            raise ValueError('{!r} is not an {!r}'.format(
                item, self.item_class))

        if self.annotations_key not in self.annotations:
            self.annotations[self.annotations_key] = PersistentList()

        item.id = self.next_id()
        self.annotations[self.annotations_key].append(item._data)
        return item

    def remove(self, item):
        self.annotations.get(self.annotations_key, []).remove(item._data)

    def next_id(self):
        id_ = self.annotations.get(self.auto_increment_annotations_key, 0) + 1
        self.annotations[self.auto_increment_annotations_key] = id_
        return id_

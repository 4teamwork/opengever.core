import csv

from zope.schema import getFieldsInOrder

from plone.i18n.normalizer import urlnormalizer
from plone.dexterity import utils

_marker = object()


def createContentInContainer(container, portal_type, checkConstraints=True, **kw):
    obj = utils.createContentInContainer(container, portal_type, checkConstraints=checkConstraints, **kw)
    update_object(obj, **kw)
    return obj

def update_object(obj, **kw):
    fields = {}
    for schemata in utils.iterSchemata(obj):
        for name, field in getFieldsInOrder(schemata):
            fields[name] = field
    for k, v in kw.items():
        if k in fields.keys():
            fields[k].set(fields[k].interface(obj), v)
        else:
            print '*** WARNING: field %s not found for object' % k, obj

class TypeGenerator(object):

    def __init__(self, setup, fileencoding='iso-8859-1'):
        self.setup = setup
        self.portal = self.setup.getSite()
        self.fileencoding = fileencoding


    def create_from_csv(self, container, portal_type, csv_stream,
                        checkConstraints=True, skip_existing_identified_by=None):
        data_rows = self._get_objects_data(csv_stream)
        print '* CREATING %s %s objects' % (len(data_rows), portal_type)
        for data in data_rows:
            obj = self._is_existing(container, portal_type,
                                    data, skip_existing_identified_by)
            if skip_existing_identified_by and obj:
                print '** already existing:', data, obj
                update_object(obj, **data)
                yield obj
            else:
                yield createContentInContainer(container=container,
                                               portal_type=portal_type,
                                               checkConstraints=checkConstraints,
                                               **data)
                print '** created:', data

    def _get_objects_data(self, csv_stream):
        csv_stream.seek(0)
        dialect = csv.Sniffer().sniff(csv_stream.read(1024))
        csv_stream.seek(0)
        rows = list(csv.DictReader(csv_stream, dialect=dialect))
        # we need to convert the values to unicode
        for row in rows:
            for key, value in row.items():
                if isinstance(value, str):
                    row[key] = unicode(value.decode(self.fileencoding))
        return rows

    def _is_existing(self, container, portal_type, data, discriminator):
        for id in container.objectIds():
            obj = container.get(id)
            if obj.portal_type!=portal_type:
                continue
            fields = self._get_all_fields_of(obj)
            if discriminator in fields.keys():
                dfield = fields.get(discriminator)
                if dfield.get(dfield.interface(obj))==data.get(discriminator):
                    return obj
        return False

    def _get_all_fields_of(self, obj):
        fields = {}
        for schemata in utils.iterSchemata(obj):
            for name, field in getFieldsInOrder(schemata):
                fields[name] = field
        return fields


class ContactGenerator(object):

    names_file = 'names.csv'
    surnames_file = 'surnames.csv'
    fileencoding = "iso-8859-1"

    def __init__(self, setup):
        self.setup = setup
        self.portal = self.setup.getSite()
        self.openDataFile = self.setup.openDataFile
        self._names = None
        self._surnames = None

    def _get_name(self):
        if not self._names:
            self._names = self.openDataFile(self.names_file)
        value = self._names.readline()
        if value:
            return unicode(value.strip().decode(self.fileencoding))
        else:
            return None

    def _get_surname(self):
        if not self._surnames:
            self._surnames = self.openDataFile(self.surnames_file)
        value = self._surnames.readline()
        if value:
            return unicode(value.strip().decode(self.fileencoding))
        else:
            return None

    def _get_userid_of(self, name, surname):
        userid = urlnormalizer.normalize(u'%s.%s' % (name, surname))
        userid = userid.replace('-', '')
        userid = userid.replace('..', '.')
        return userid

    def get_contact_data(self):
        name = self._get_name()
        surname = self._get_surname()
        if not name or not surname:
            return None
        userid = self._get_userid_of(name, surname)
        email = '%s@4teamwork.ch' % userid
        return {
            'lastname' : surname,
            'firstname' : name,
            'email' : email,
            'userid' : userid,
            }

    def list_contact_data(self):
        next = self.get_contact_data()
        while next:
            yield next
            next = self.get_contact_data()

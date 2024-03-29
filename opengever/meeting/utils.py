from opengever.base.date_time import ulocalized_time
from opengever.meeting.interfaces import IMeetingSettings
from plone import api
from zope.globalrequest import getRequest


class JsonDataProcessor(object):
    """ Used to process json data before submitting it
    to sablon templates.
    """

    def _recursive_transform(self, obj, key_list, transform):
        if obj and isinstance(key_list, tuple):
            if len(key_list) > 1:
                return self._recursive_transform(obj.get(key_list[0]), key_list[1:], transform)
            elif obj.get(key_list[0]):
                obj[key_list[0]] = transform(obj[key_list[0]])
            return

    def process(self, data, field_list, transform_list):
        """
        Because of the nested structure of json data, fields that should
        be processed are passed to the process method as a tuple of keys
        and searched for recursively. For each of these fields a transform
        function should be passed in transform_list.
        """
        for field, transform in zip(field_list, transform_list):
            self._recursive_transform(data, field, transform)
        return data


def format_date(date, request=None):
    if request is None:
        request = getRequest()
    date_string_format = api.portal.get_registry_record(
        "sablon_date_format_string", interface=IMeetingSettings)
    return ulocalized_time(date, date_string_format, request)


def is_docx(document):
    document_file = document.get_file()
    if not document_file:
        return False
    document_mimetype = document_file.contentType
    docx_mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    return document_mimetype == docx_mimetype


def disable_meeting_feature():
    api.portal.set_registry_record(
        'is_feature_enabled', False, interface=IMeetingSettings)
    catalog = api.portal.get_tool('portal_catalog')
    for brain in catalog.unrestrictedSearchResults(
            portal_type='opengever.meeting.committeecontainer'):
        brain.getObject().reindexObject(idxs=['exclude_from_nav'])

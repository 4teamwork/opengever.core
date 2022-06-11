from opengever.oneoffixx.utils import whitelisted_template_types
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from zope.component import getUtility


def get_whitelisted_oneoffixx_templates(api_client):
    return [
        OneOffixxTemplate(template, template_group.get('localizedName', ''))
        for template_group in api_client.get_oneoffixx_template_groups()
        for template in template_group.get("templates")
        if template.get('metaTemplateId') in whitelisted_template_types
    ]


def get_oneoffixx_favorites(api_client):
    return [
        OneOffixxTemplate(template) for template in
        api_client.get_oneoffixx_favorites()
        if template.get(u'metaTemplateId') in whitelisted_template_types
    ]


def get_oneoffixx_template_groups(api_client):
    return [
        OneOffixxTemplateGroup(group) for group in
        api_client.get_oneoffixx_template_groups()
    ]


class OneOffixxTemplate(object):

    def __init__(self, template, groupname=''):
        self.title = template.get("localizedName")
        self.template_id = template.get("id")
        self.group = template.get('templateGroupId')
        self.groupname = groupname
        template_type = template['metaTemplateId']
        template_type_info = whitelisted_template_types[template_type]
        self.content_type = template_type_info['content-type']
        filename = template.get("localizedName")
        normalizer = getUtility(IFileNameNormalizer, name='gever_filename_normalizer')
        self.filename = normalizer.normalize(filename, extension=template_type_info['extension'])
        self.languages = template.get("languages")

    def __eq__(self, other):
        if type(other) == type(self):
            return self.template_id == other.template_id
        return False

    def json(self):
        return {
            "title": self.title,
            "template_id": self.template_id,
            "content_type": self.content_type,
            "filename": self.filename,
        }


class OneOffixxTemplateGroup(object):

    def __init__(self, group):
        self.title = group.get('localizedName')
        self.group_id = group.get('id')
        self.templates = [template.get('id') for template in group.get('templates')]

    def json(self):
        return {
            "title": self.title,
            "group_id": self.group_id,
            "templates": self.templates,
        }

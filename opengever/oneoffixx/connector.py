from plone import api
from plone.memoize import ram
from time import time
import requests


class OneOffixxAPIException(Exception):
    """Exception which happen during OneOffix API requests.
    """


def oneoffix_templates_cache_key(method, *args):
    """User specific cache key for the oneoffix template getter,
    invalidates all hours.
    """
    return "{}.{}:{}:{}".format(
        method.__module__, method.__name__,
        api.user.get_current().getId(),
        time() // (60 * 60))


class OneOffixConnector(object):

    base_api_url = 'https://o10002.oneoffixx.com/webapi/api/v1'

    def get_authorization_token(self):
        # TODO: Implement oauth authorization
        return 'REPLACE Me with token'

    def get_header(self):
        return {
            'Coontent-type': "application/json",
            'Authorization': 'Bearer {}'.format(self.get_authorization_token())}

    def get_data_source_id(self):
        endpoint = 'TenantInfo'
        url = '/'.join((self.base_api_url, endpoint))
        response = requests.get(url, headers=self.get_header())

        if response.status_code != 200:
            raise OneOffixxAPIException(
                'Could not load templates from OneOffix API')

        datasources = response.json()[0].get('datasources')
        if not datasources:
            raise OneOffixxAPIException('No datasources available')

        # We currently not support mutltiple datasources
        self.datasource = datasources[0]
        return datasources[0]['id']

    @ram.cache(oneoffix_templates_cache_key)
    def get_template_groups(self):
        url = '/'.join((self.base_api_url, self.get_data_source_id(),
                        'TemplateLibrary/TemplateGroups'))

        response = requests.get(url, headers=self.get_header())
        return response.json()

from ftw.solr.interfaces import ISolrSearch
from opengever.base.interfaces import ISearchSettings
from plone import api
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import getUtility


class SolrSearchGet(Service):
    """REST API endpoint to querying SOLR
    """

    DEFAULT_RESULT_FIELDS = ['UID', 'Title', 'Description', 'path']
    NOT_SUPPORTED_FIELDS = ['SearchableText', 'allowedRolesAndUsers']
    SUPPORTED_PARAMETERS = {
        'q': 'query',
        'fq': 'filters',
        'start': 'start',
        'rows': 'rows',
        'sort': 'sort'}

    def reply(self):
        if not api.portal.get_registry_record(
                'use_solr', interface=ISearchSettings):
            raise BadRequest('Solr is not enabled on this GEVER installation.')

        kwargs = self.request.form
        kwargs['fl'] = self.update_fields(kwargs.get('fl'))

        for request_name, utility_name in self.SUPPORTED_PARAMETERS.items():
            if request_name in kwargs:
                kwargs[utility_name] = kwargs.pop(request_name)

        solr = getUtility(ISolrSearch)
        res = solr.search(**kwargs)
        return res.docs

    def update_fields(self, field_string):
        if not field_string:
            fields = self.DEFAULT_RESULT_FIELDS
        else:
            fields = field_string.split(',')

        return ','.join(
            [field for field in fields if field not in self.NOT_SUPPORTED_FIELDS])

from os import environ
import logging
import requests


logger = logging.getLogger('opengever.disposition.archive_clients')


class NullClient(object):
    """Client which does nothing and can be used for testing
    """
    def deliver(self, *args, **kwargs):
        return None, '0'


class DocuteamClient(object):
    def __init__(self):
        self.ingest_url = environ.get('DISPOSITION_DOCUTEAM_INGEST_URL')
        if not self.ingest_url:
            raise ValueError('Missing required environment variable: DISPOSITION_DOCUTEAM_INGEST_URL')

        self.api_key = environ.get('DISPOSITION_DOCUTEAM_INGEST_API_KEY')
        if not self.api_key:
            raise ValueError('Missing required environment variable: DISPOSITION_DOCUTEAM_INGEST_API_KEY')

    def deliver(self, sip_package, filename='package.zip'):
        url = '{}?token={}&format=ech0160'.format(
            self.ingest_url, self.api_key)
        response = requests.post(
            url,
            files={'package': (filename, sip_package.data, 'application/zip')},
        )
        response.raise_for_status()
        try:
            submission_id = response.json()['response'][0]['id']
        except (ValueError, KeyError, IndexError):
            submission_id = u'<unavailable>'
        logger.info('SIP delivered to docuteam archive. Submission ID: %s', submission_id)
        return response, submission_id


archive_client_registry = {
    'null_client': NullClient,
    'docuteam': DocuteamClient,
}


def get_archive_client():
    provider_name = environ.get('DISPOSITION_SIP_TO_ARCHIVE_PROVIDER', '').strip().lower()
    if not provider_name:
        raise ValueError('Unknown disposition archive provider configured')
    return archive_client_registry[provider_name]()

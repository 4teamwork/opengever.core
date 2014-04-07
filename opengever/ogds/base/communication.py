"""Tools for communicating between clients.
"""


from five import grok
from opengever.ogds.base.interfaces import IClientCommunicator
from opengever.ogds.base.utils import remote_json_request


class ClientCommunicator(grok.GlobalUtility):
    """The ClientCommunicator utility communicates with other clients.
    """

    grok.provides(IClientCommunicator)

    def get_open_dossiers(self, target_client_id):
        """ Returns a list of open dossiers hosted on a remote client
        [
        {
        'url' : 'http://nohost/other-client/op1/op2/dossier1',
        'path' : 'op1/op2/dossier1',
        'title' : 'Dossier 1',
        'workflow_state' : DOSSIER_STATES_OPEN,
        'reference_number' : 'OG 1.2 / 1',
        }
        ]
        """

        return remote_json_request(target_client_id,
                                   '@@list-open-dossiers-json')

    def get_documents_of_dossier(self, target_client_id, dossier_path):
        """ Returns a list of dicts representing documents located in a
        specific dossier on a remote client
        Keys of the dict:
        * path
        * url
        * title
        * review_state
        """

        return remote_json_request(target_client_id,
                                   '@@tentacle-documents-of-dossier-json',
                                   data=dict(dossier=dossier_path))

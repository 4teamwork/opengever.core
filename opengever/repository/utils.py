from Acquisition import aq_chain
from opengever.repository.repositoryroot import IRepositoryRoot


def is_within_repository(context):
    """ Checks, if the content is within the repository.
    """

    return bool(filter(IRepositoryRoot.providedBy, aq_chain(context)))

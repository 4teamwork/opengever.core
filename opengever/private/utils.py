from Acquisition import aq_chain
from opengever.private.root import IPrivateRoot


def is_within_private_root(context):
    """ Checks, if the content is within the private root.
    """

    return bool(filter(IPrivateRoot.providedBy, aq_chain(context)))

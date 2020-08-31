from zope.globalrequest import getRequest
import itertools


def txn_is_dirty():
    """Determines whether the current transaction has changes or not.
    """
    return bool(registered_objects())


def registered_objects():
    """Returns a list of objects changed in this transaction.

    Lifted from plone.protect.auto.
    """
    app = getRequest().PARENTS[-1]
    return list(itertools.chain.from_iterable([
        conn._registered_objects
        # skip the 'temporary' connection since it stores session objects
        # which get written all the time
        for name, conn in app._p_jar.connections.items()
        if name != 'temporary'
    ]))

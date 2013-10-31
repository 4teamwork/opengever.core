from Products.CMFCore.utils import getToolByName
from opengever.ogds.base.interfaces import IContactInformation
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
import types


def get_selected_items_from_catalog(context, request):
    """Returns a set of brains.
    """

    paths = request.get('paths', None)

    if paths:
        catalog = getToolByName(context, 'portal_catalog')

        for path in request.get('paths', []):
            brains = catalog({'path': {'query': path,
                                       'depth': 0}})
            assert len(brains) == 1, "Could not find objects at %s" % path
            yield brains[0]


def get_responsible_of_task(task):
    info = getUtility(IContactInformation)

    return '{} / {}'.format(
        info.get_client_by_id(task.assigned_client).title,
        info.describe(task.responsible, with_principal=False))


def get_issuer_of_task(task, with_client=True, with_principal=False):
    info = getUtility(IContactInformation)

    issuer = info.describe(task.issuer, with_principal=with_principal)

    if not with_client:
        return issuer

    if task.predecessor and isinstance(task.predecessor, types.StringTypes):
        # task is a brain or a task object -> predecessor is the oguid
        issuer_client_id = task.predecessor.split(':')[0]

    elif task.predecessor:
        # task is a globalindex object -> predecessor is a globalindex obj too
        issuer_client_id = task.predecessor.client_id

    else:
        issuer_client_id = task.client_id

    issuer_client_title = info.get_client_by_id(issuer_client_id).title

    return '%s / %s' % (issuer_client_title, issuer)


def workflow_state(item, value):
    """Helper which translates the workflow_state in plone domain
    """

    # We use zope.globalrequest because item can be a SQLAlchemy `Task` object
    # which doesn't have a request
    request = getRequest()
    return """%s""" % (translate(value, domain='plone', context=request))

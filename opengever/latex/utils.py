from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import ogds_service
from Products.CMFCore.utils import getToolByName
from zope.globalrequest import getRequest
from zope.i18n import translate
from opengever.base.utils import rewrite_path_list_to_absolute_paths


def get_selected_items_from_catalog(context, request):
    """Returns a set of brains.
    """

    rewrite_path_list_to_absolute_paths(request)
    paths = request.get('paths', None)

    if paths:
        catalog = getToolByName(context, 'portal_catalog')

        for path in request.get('paths', []):
            brains = catalog({'path': {'query': path,
                                       'depth': 0}})
            assert len(brains) == 1, "Could not find objects at %s" % path
            yield brains[0]


def get_responsible_of_task(task):
    actor = Actor.lookup(task.responsible)
    org_unit = ogds_service().fetch_org_unit(task.assigned_org_unit)
    return org_unit.prefix_label(
        actor.get_label(with_principal=False))


# XXX rework this helper, hopefully id should not be necessary anymore
def get_issuer_of_task(task, with_client=True, with_principal=False):

    issuer = Actor.lookup(task.issuer)

    if not with_client:
        return issuer.get_label(with_principal=with_principal)

    if task.predecessor:
        issuing_unit_id = task.predecessor.issuing_org_unit
    else:
        issuing_unit_id = task.issuing_org_unit

    org_unit = ogds_service().fetch_org_unit(issuing_unit_id)
    return org_unit.prefix_label(
        issuer.get_label(with_principal=with_principal))


def workflow_state(item, value):
    """Helper which translates the workflow_state in plone domain
    """

    # We use zope.globalrequest because item can be a SQLAlchemy `Task` object
    # which doesn't have a request
    request = getRequest()
    return """%s""" % (translate(value, domain='plone', context=request))

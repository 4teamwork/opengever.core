from opengever.quota.sizequota import size_quotas_in_chain_of
from zope.container.interfaces import IContainerModifiedEvent


def update_size_usage_for_object(context, event):
    if IContainerModifiedEvent.providedBy(event):
        return

    for size_quota in size_quotas_in_chain_of(context):
        size_quota.update_object_usage(context)


def update_size_usage_when_moving_object(context, event):
    if event.oldParent:
        for size_quota in size_quotas_in_chain_of(event.oldParent):
            size_quota.remove_object_usage(context)

    if event.newParent:
        for size_quota in size_quotas_in_chain_of(event.newParent):
            size_quota.update_object_usage(context)

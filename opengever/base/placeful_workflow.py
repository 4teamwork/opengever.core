from plone import api


def assign_placeful_workflow(obj, policy_name):
    """Assign placeful workflow policy to obj (in and below).

    Assign the placeful workflow policy identified by `policy_name` to the
    object `obj`. The same policy is added in the object and below the object
    as we currently only define such placeful workflow policies.
    """
    policy_in = policy_name
    policy_below = policy_name

    placeful_workflow = api.portal.get_tool('portal_placeful_workflow')
    config = placeful_workflow.getWorkflowPolicyConfig(obj)

    if not config:
        obj.manage_addProduct[
            'CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
        config = placeful_workflow.getWorkflowPolicyConfig(obj)

    config.setPolicyIn(policy=policy_in, update_security=True)
    config.setPolicyBelow(policy=policy_below, update_security=True)

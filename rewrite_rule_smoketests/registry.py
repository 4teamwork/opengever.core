"""Registry that keeps track of tests that get registered via decorators.
"""

# For a test to be run, it needs to be registered for either the
# 'cluster' or the 'admin_unit' type. It will then be invoked by then runner
# with its second argument being an entity of that type (AdminUnit or Cluster).
# Tests can also be registered for both - which will run them twice.
#
# The @logged_in decorator can be used in addition to those. It will make
# sure that the runner attempts to provide the browser with a valid portal
# session before handing it to the test.
tests_by_type = {
    'cluster': [],
    'admin_unit': [],
    'logged_in': [],
}


def on_cluster(func):
    tests_by_type['cluster'].append(func)
    return func


def on_admin_unit(func):
    tests_by_type['admin_unit'].append(func)
    return func


def logged_in(func):
    tests_by_type['logged_in'].append(func)
    return func

from pkg_resources import resource_filename


def get_path(name):
    return resource_filename('opengever.bundle.tests.assets', name)

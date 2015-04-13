from pkg_resources import resource_string


def load(asset_filename):
    return resource_string('opengever.testing.assets', asset_filename)

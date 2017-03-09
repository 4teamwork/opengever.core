from Products.CMFCore.utils import getToolByName


def policy_installed(site):
    configure_error_log(site)


def configure_error_log(site):
    error_log = getToolByName(site, 'error_log')
    properties = error_log.getProperties()
    if 'ForbiddenByQuota' in properties.get('ignored_exceptions', ()):
        return

    properties['ignored_exceptions'] += ('ForbiddenByQuota',)
    error_log.setProperties(**properties)

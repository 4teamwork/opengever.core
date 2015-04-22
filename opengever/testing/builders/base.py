import pkg_resources

try:
    pkg_resources.get_distribution('plone.app.testing')
    from plone.app.testing import TEST_USER_ID
except pkg_resources.DistributionNotFound:
    TEST_USER_ID = 'ogadmin'

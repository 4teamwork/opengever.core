from opengever.repository.interfaces import IRepositoryFolderRecords
from zope.component import getUtility
from plone.registry.interfaces import IRegistry


def getAlternativeLanguageCode():
    """ Gets configured alternative language code from registry.
    Used for livesearch view because of the security limitations.
    Returns code as string or None if not configured.
    """

    registry = getUtility(IRegistry)
    reg_proxy = registry.forInterface(IRepositoryFolderRecords)
    return reg_proxy.alternative_language_code


def getPrimaryLanguageCode():
    """ Gets configured primary language code from registry.
    Returns string. Default is 'de'.
    """

    registry = getUtility(IRegistry)
    reg_proxy = registry.forInterface(IRepositoryFolderRecords)
    return reg_proxy.primary_language_code

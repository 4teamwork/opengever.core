from zope.i18nmessageid import MessageFactory
from AccessControl.SecurityInfo import ModuleSecurityInfo

_ = MessageFactory('opengever.repository')

security = ModuleSecurityInfo('opengever.repository.utils')
security.declarePublic('getAlternativeLanguageCode')

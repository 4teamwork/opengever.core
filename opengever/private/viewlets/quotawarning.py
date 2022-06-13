from Acquisition import aq_chain
from opengever.private import _
from opengever.private.folder import IPrivateFolder
from opengever.quota.interfaces import HARD_LIMIT_EXCEEDED
from opengever.quota.interfaces import SOFT_LIMIT_EXCEEDED
from opengever.quota.sizequota import ISizeQuota
from plone.app.caching.interfaces import IETagValue
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface


def get_quota_warning_type_to_show_in(context):
    private_folders = filter(IPrivateFolder.providedBy, aq_chain(context))

    if not private_folders:
        return None

    private_folder, = private_folders

    return ISizeQuota(private_folder).exceeded_limit()


class QuotaWarningViewlet(ViewletBase):
    """Provide a warning viewlet for exceeding private folder quotas."""

    index = ViewPageTemplateFile('templates/quotawarning.pt')

    def get_message_to_show(self):
        warning_type = get_quota_warning_type_to_show_in(self.context)
        if warning_type == HARD_LIMIT_EXCEEDED:
            return {
                'type': 'error',
                'message': _(
                    u'The quota of your private folder has exceeded, you can '
                    u'not add any new files or mails.',
                ),
            }

        elif warning_type == SOFT_LIMIT_EXCEEDED:
            return {
                'type': 'warning',
                'message': _(
                    u'The quota of your private folder will exceed soon.',
                ),
            }

        return None


class QuotaWarningETagValue(object):
    """Provide ETags for per user caching of quota warnings."""

    implements(IETagValue)
    adapts(Interface, Interface)

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def __call__(self):
        warning_type = get_quota_warning_type_to_show_in(self.published)

        if warning_type == HARD_LIMIT_EXCEEDED:
            return 'h'

        elif warning_type == SOFT_LIMIT_EXCEEDED:
            return 's'

        return '-'

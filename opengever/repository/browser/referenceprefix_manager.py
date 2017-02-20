from opengever.base.adapters import ReferenceNumberPrefixAdpater
from opengever.repository import _
from opengever.repository.events import RepositoryPrefixUnlocked
from plone import api
from zope.event import notify
from zope.publisher.browser import BrowserView


class ReferencePrefixManager(BrowserView):

    def __call__(self, *args, **kwargs):
        prefix_num = self.request.get('prefix')
        if prefix_num:
            self.free_reference_prefix(prefix_num)

        return super(ReferencePrefixManager, self).__call__(*args, **kwargs)

    def free_reference_prefix(self, prefix_num):
        refs = ReferenceNumberPrefixAdpater(self.context)

        if refs.is_prefix_used(prefix_num):
            api.portal.show_message(
                _(u'statmsg_prefix_unlock_failure',
                  default='The reference you try to unlock is still in use.'),
                request=self.request,
                type="error")
            return

        refs.free_number(prefix_num)
        notify(RepositoryPrefixUnlocked(self.context, prefix_num))
        api.portal.show_message(
            _("statmsg_prefix_unlocked",
              default=u"Reference prefix has been unlocked."),
            request=self.request,
            type="info")

    def prefix_mapping(self):
        refs = ReferenceNumberPrefixAdpater(self.context)
        return refs.get_number_mapping()

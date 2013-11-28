from opengever.base.adapters import ReferenceNumberPrefixAdpater
from opengever.repository import _
from opengever.repository.events import RepositoryPrefixUnlocked
from Products.statusmessages.interfaces import IStatusMessage
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
        refs.free_number(prefix_num)

        notify(RepositoryPrefixUnlocked(self.context, prefix_num))
        messages = IStatusMessage(self.request)
        messages.add(_("statmsg_prefix_unlocked",
                    default=u"Reference prefix has been unlocked."),
                    type=u"info")

    def prefix_mapping(self):
        refs = ReferenceNumberPrefixAdpater(self.context)
        return refs.get_number_mapping()

from five import grok
from opengever.base.adapters import ReferenceNumberPrefixAdpater
from opengever.repository import _
from opengever.repository.interfaces import IRepositoryFolder
from Products.statusmessages.interfaces import IStatusMessage


class ReferencePrefixManager(grok.View):
    grok.context(IRepositoryFolder)
    grok.name("referenceprefix_manager")
    grok.require("zope2.View") # TODO set correct permissions

    def update(self):
        refs = ReferenceNumberPrefixAdpater(self.context)

        if self.request.get('prefix'):
            refs.free_number(self.request.get('prefix'))
            messages = IStatusMessage(self.request)
            messages.add(_("statmsg_prefix_unlocked", # TODO add translation
                        default=u"Reference prefix has been unlocked."),
                        type=u"info")

    def prefix_mapping(self):
        refs = ReferenceNumberPrefixAdpater(self.context)
        return refs.get_number_mapping()

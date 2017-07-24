from ftw.zipexport.representations import dexterity
from opengever.mail.mail import IOGMail
from opengever.mail.mail import IOGMailMarker
from zope.component import adapts
from zope.interface import Interface
from ftw.zipexport.events import ItemZippedEvent
from zope.event import notify


class OGMailZipExport(dexterity.DexterityItemZipRepresentation):
    adapts(IOGMailMarker, Interface)

    def get_files(self, *args, **kwargs):
        ogmail = IOGMail(self.context)
        if ogmail.original_message:
            notify(ItemZippedEvent(self.context))

            yield self.get_file_tuple(ogmail.original_message,
                                      kwargs.get('path_prefix', ''))

        else:
            for item in super(OGMailZipExport, self).get_files(
                    *args, **kwargs):

                yield item

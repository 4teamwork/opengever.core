from ftw.zipexport.events import ItemZippedEvent
from ftw.zipexport.representations import dexterity
from opengever.mail.mail import IOGMailMarker
from zope.component import adapts
from zope.event import notify
from zope.interface import Interface


class OGMailZipExport(dexterity.DexterityItemZipRepresentation):
    adapts(IOGMailMarker, Interface)

    def get_files(self, *args, **kwargs):
        notify(ItemZippedEvent(self.context))
        yield self.get_file_tuple(self.context.get_file(),
                                  kwargs.get('path_prefix', ''))

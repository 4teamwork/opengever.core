from opengever.base.addressblock.interfaces import IAddressBlockData
from opengever.base.docprops import BaseDocPropertyProvider
from opengever.ogds.models.user import User
from zope.component import adapter
from zope.component import queryAdapter


@adapter(User)
class OGDSUserDocPropertyProvider(BaseDocPropertyProvider):

    def get_properties(self, prefix=None):
        properties = {}
        address_block = queryAdapter(self.context, IAddressBlockData)
        if address_block:
            key = '.'.join(filter(None, ['ogg', prefix, 'address.block']))
            properties.update({key: address_block.format()})
        return properties

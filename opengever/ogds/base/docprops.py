from opengever.base.addressblock.docprops import get_addressblock_docprops
from opengever.base.docprops import BaseDocPropertyProvider
from opengever.ogds.models.user import User
from zope.component import adapter


@adapter(User)
class OGDSUserDocPropertyProvider(BaseDocPropertyProvider):

    def get_properties(self, prefix=None):
        return get_addressblock_docprops(self.context, prefix)

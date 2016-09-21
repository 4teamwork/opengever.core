from opengever.officeatwork import is_officeatwork_feature_enabled
from opengever.officeatwork.ocmfile import OCMFile
from Products.Five import BrowserView
from zExceptions import Unauthorized


class CreateWithOfficeatwork(BrowserView):
    """View to download the ocm file for officeatwork."""

    def __call__(self):
        if not is_officeatwork_feature_enabled():
            raise Unauthorized

        ocmfile = OCMFile.for_officeatwork(self.context)
        if not ocmfile:
            raise Unauthorized

        return ocmfile.dump()

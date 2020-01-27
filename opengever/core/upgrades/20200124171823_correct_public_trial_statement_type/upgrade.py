from Acquisition import aq_base
from DateTime import DateTime
from ftw.upgrade import UpgradeStep
from Products.CMFDiffTool.utils import safe_utf8
import pkg_resources


class CorrectPublicTrialStatementType(UpgradeStep):
    """Correct public_trial_statement type.

    On some older objects public_trial_statement is saved as unicode
    on the object which will lead to errors if it contains non ASCII
    characters.
    We did not determine in which commit this was fixed and even
    then we would still need to find out for each deployment when that
    fix was introduced. Nevertheless we only fix objects older than 2016
    as this seems to be a problem only for Zug, and it seems the issue was
    fixed there mid 2015.
    """

    deferrable = True

    def __call__(self):
        # we only run this upgrade for Zug for now.
        try:
            pkg_resources.get_distribution('opengever.zug')
        except pkg_resources.DistributionNotFound:
            return

        query = {'portal_type': ['opengever.document.document', 'ftw.mail.mail'],
                 'created': {'query': DateTime('2016-01-01'),
                             'range': 'max'}}

        for obj in self.objects(query, 'Correct public_trial_statement type'):
            # We only need to correct the field if it is not empty and this way
            # we avoid casting None to a string.
            pts_value = getattr(aq_base(obj), 'public_trial_statement', None)
            if pts_value and isinstance(pts_value, unicode):
                obj.public_trial_statement = safe_utf8(pts_value)

from ftw.upgrade import UpgradeStep
from opengever.base.hooks import register_trix_to_sablon_transform


class AddTrixHtmlToSablonHtmlTransform(UpgradeStep):
    """Add trix_html_to_sablon_html transform.
    """

    def __call__(self):
        register_trix_to_sablon_transform()

import pkg_resources
from opengever.bumblebee import is_bumblebee_feature_enabled


try:
    pkg_resources.get_distribution('opengever.pdfconverter')
except pkg_resources.DistributionNotFound:
    PDFCONVERTER_AVAILABLE = False
else:
    PDFCONVERTER_AVAILABLE = True


def is_pdfconverter_enabled():
    return PDFCONVERTER_AVAILABLE and not is_bumblebee_feature_enabled()

import pkg_resources
from opengever.bumblebee import is_bumblebee_feature_enabled


try:
    pkg_resources.get_distribution('opengever.pdfconverter')
except pkg_resources.DistributionNotFound:
    print("Failed to import opengever.pdfconverter, setting "
          "PDFCONVERTER_AVAILABLE to False")
    PDFCONVERTER_AVAILABLE = False
else:
    print("Successfully imported opengever.pdfconverter, setting "
          "PDFCONVERTER_AVAILABLE to True")

    PDFCONVERTER_AVAILABLE = True


def is_pdfconverter_enabled():
    print ("PDFCONVERTER_AVAILABLE: %r") % PDFCONVERTER_AVAILABLE
    return PDFCONVERTER_AVAILABLE and not is_bumblebee_feature_enabled()

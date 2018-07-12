import pkg_resources
import threading


try:
    pkg_resources.get_distribution('opengever.pdfconverter')
except pkg_resources.DistributionNotFound:
    PDFCONVERTER_AVAILABLE = False
else:
    PDFCONVERTER_AVAILABLE = True


# Lock used by context manager in og.core.testing to manage safe monkey
# patching of PDFCONVERTER_AVAILABLE flag
pdfconverter_available_lock = threading.Lock()

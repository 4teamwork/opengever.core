from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup

@onsetup
def setupPackage():
    fiveconfigure.debug_mode = True
    import ftw.task
    zcml.load_config('configure.zcml', ftw.task)
    fiveconfigure.debug_mode = False
    #ztc.installPackage('ftw.task')

setupPackage()
PloneTestCase.setupPloneSite()

class TestCase(PloneTestCase.PloneTestCase):
    """Base class for integration tests
    """
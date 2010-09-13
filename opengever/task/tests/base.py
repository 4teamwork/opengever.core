# from Testing import ZopeTestCase as ztc
from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup


@onsetup
def setupPackage():
    fiveconfigure.debug_mode = True
    import opengever.task
    zcml.load_config('configure.zcml', opengever.task)
    fiveconfigure.debug_mode = False
    #ztc.installPackage('opengever.task')


setupPackage()
PloneTestCase.setupPloneSite()


class TestCase(PloneTestCase.PloneTestCase):
    """Base class for integration tests
    """

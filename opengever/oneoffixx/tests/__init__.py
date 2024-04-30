from opengever.testing import IntegrationTestCase


class BaseOneOffixxTestCase(IntegrationTestCase):

    features = ("officeconnector-checkout", "oneoffixx")



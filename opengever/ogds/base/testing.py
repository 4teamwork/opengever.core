from opengever.ogds.base.setuphandlers import create_sql_tables, MODELS
from opengever.ogds.base.utils import create_session
from plone.app.testing import PLONE_FIXTURE
from plone.testing import Layer
from zope.configuration import xmlconfig


class BaseLayer(Layer):

    defaultBases = (PLONE_FIXTURE, )

    def testSetUp(self):
        # Load test.zcml
        import opengever.ogds.base
        xmlconfig.file('test.zcml', opengever.ogds.base)
        # setup the sql tables
        create_sql_tables()

    def testTearDown(test):
        session = create_session()
        for model in MODELS:
            getattr(model, 'metadata').drop_all(session.bind)


OPENGEVER_OGDS_BASE_FIXTURE = BaseLayer()

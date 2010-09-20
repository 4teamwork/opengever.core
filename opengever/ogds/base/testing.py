# from plone.testing import Layer
# from plone.testing.zca import UNIT_TESTING
# from plone.testing.zca import ZCML_DIRECTIVES
# from zope.configuration import xmlconfig
# from opengever.ogds.base.setuphandlers import create_sql_tables


# class SqlLayer(Layer):

#     defaultBases = (UNIT_TESTING, ZCML_DIRECTIVES)

#     def setUp(self):
#         # Load test.zcml
#         import opengever.ogds.base
#         xmlconfig.file('test.zcml', opengever.ogds.base)
#         # setup the sql tables
#         create_sql_tables()


# OPENGEVER_OGDS_BASE_SQL = SqlLayer()

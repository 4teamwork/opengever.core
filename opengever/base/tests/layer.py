# from opengever.ogds.base.setuphandlers import create_sql_tables
# from opengever.ogds.base.setuphandlers import _create_example_client
# from opengever.ogds.base.utils import create_session
from plone.directives import form
# from Products.PloneTestCase import ptc
# import collective.testcaselayer.ptc
# 
# 
# ptc.setupPloneSite()
# 
# class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):
# 
#     def afterSetUp(self):
# 
#         from plone.app import dexterity
#         self.loadZCML('meta.zcml', package=dexterity)
#         self.loadZCML('configure.zcml', package=dexterity)
#         self.addProfile('plone.app.dexterity:default')
# 
#         from opengever.ogds import base
#         self.loadZCML('tests.zcml', package=base)
#         self.loadZCML('configure.zcml', package=base)
#         self.addProfile('opengever.base:default')
# 
#         from opengever import repository
#         self.loadZCML('configure.zcml', package=repository)
#         self.addProfile('opengever.repository:default')
# 
#         from opengever import document
#         self.loadZCML('configure.zcml', package=document)
#         self.addProfile('opengever.document:default')
# 
#     def testSetUp(self):
#         # setup the sql tables
#         create_sql_tables()
#         session = create_session()
# 
#         _create_example_client(session, 'plone',
#                               {'title': 'Plone',
#                               'ip_address': '127.0.0.1',
#                               'site_url': 'http://nohost/plone',
#                               'public_url': 'http://nohost/plone',
#                               'group': 'og_mandant1_users',
#                               'inbox_group': 'og_mandant1_inbox'})
# 
# base_integration_layer = IntegrationTestLayer(bases=[collective.testcaselayer.ptc.ptc_layer])

class IEmptySchema(form.Schema):
    """an empty schema used or tests"""
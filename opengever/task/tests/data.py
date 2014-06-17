from plone.app.testing import TEST_USER_ID
import json


DOCUMENT_EXTRACTION = json.dumps(
[{u'unicode:dublin-core': {u'utf8:created': u'utf8:2012/10/19 15:57:30.879365 GMT+2',
                           u'utf8:creator': u'utf8:zopemaster'},
  u'unicode:field-data': {u'utf8:IClassification': {u'utf8:classification': u'unicode:unprotected',
                                                    u'utf8:privacy_layer': u'unicode:privacy_layer_no',
                                                    u'utf8:public_trial': u'unicode:unchecked',
                                                    u'utf8:public_trial_statement': u'unicode:'},
                          u'utf8:ICreator': {u'utf8:creators': []},
                          u'utf8:IDocumentSchema': {u'utf8:file': {u'utf8:data': u'utf8:test data',
                                                                   u'utf8:filename': u'unicode:test.txt'},
                                                    u'utf8:title': u'unicode:test'},
                          u'utf8:IDocumentMetadata': {u'utf8:digitally_available': True,
                                                      u'utf8:preserved_as_paper': True,
                                                      u'utf8:archival_file': None,
                                                      u'utf8:delivery_date': None,
                                                      u'utf8:description': None,
                                                      u'utf8:document_author': None,
                                                      u'utf8:document_date': u'utf8:2012-10-19',
                                                      u'utf8:document_type': None,
                                                      u'utf8:foreign_reference': None,
                                                      u'utf8:keywords': [],
                                                      u'utf8:preview': None,
                                                      u'utf8:receipt_date': None,
                                                      u'utf8:thumbnail': None},
                          u'utf8:IRelatedDocuments': {u'utf8:relatedItems': []},
                          u'utf8:IVersionable': {u'utf8:changeNote': u'utf8:'}},
  u'unicode:intid-data': 389258091,
  u'utf8:basedata': {u'utf8:id': u'utf8:document-10',
                     u'utf8:portal_type': u'utf8:opengever.document.document',
                     u'utf8:title': u'utf8:test'}}]
)


TASK_EXTRACTION = json.dumps(
{u'unicode:dublin-core': {u'utf8:created': u'utf8:2012/10/19 15:40:19.649945 GMT+2',
                          u'utf8:creator': u'utf8:zopemaster'},
 u'unicode:field-data': {u'utf8:ITask': {u'utf8:date_of_completion': None,
                                         u'utf8:deadline': u'utf8:2012-10-24',
                                         u'utf8:effectiveCost': None,
                                         u'utf8:effectiveDuration': None,
                                         u'utf8:expectedCost': None,
                                         u'utf8:expectedDuration': None,
                                         u'utf8:expectedStartOfWork': None,
                                         u'utf8:issuer': u'unicode:testuser2',
                                         u'utf8:predecessor': None,
                                         u'utf8:relatedItems': [],
                                         u'utf8:responsible': u'unicode:%s' % TEST_USER_ID,
                                         u'utf8:responsible_client': u'unicode:plone',
                                         u'utf8:task_type': u'utf8:approval',
                                         u'utf8:text': None,
                                         u'utf8:title': u'unicode:Testaufgabe'}},
 u'unicode:intid-data': 389258089,
 u'utf8:basedata': {u'utf8:id': u'utf8:task-1',
                    u'utf8:portal_type': u'utf8:opengever.task.task',
                    u'utf8:title': u'utf8:Testaufgabe'}}
)


FORWARDING_EXTRACTION = json.dumps(
{u'unicode:dublin-core': {u'utf8:created': u'utf8:2012/10/19 15:58:8.235873 GMT+2',
                          u'utf8:creator': u'utf8:zopemaster'},
 u'unicode:field-data': {u'utf8:IForwarding': {u'utf8:date_of_completion': None,
                                               u'utf8:deadline': u'utf8:2012-10-24',
                                               u'utf8:effectiveCost': None,
                                               u'utf8:effectiveDuration': None,
                                               u'utf8:expectedCost': None,
                                               u'utf8:expectedDuration': None,
                                               u'utf8:expectedStartOfWork': None,
                                               u'utf8:issuer': u'unicode:inbox:client2',
                                               u'utf8:predecessor': None,
                                               u'utf8:relatedItems': [],
                                               u'utf8:responsible': u'unicode:inbox:plone',
                                               u'utf8:responsible_client': u'unicode:plone',
                                               u'utf8:task_type': u'utf8:forwarding_task_type',
                                               u'utf8:text': None,
                                               u'utf8:title': u'unicode:Ein Testdokument'}},
 u'unicode:intid-data': 389258092,
 u'utf8:basedata': {u'utf8:id': u'utf8:forwarding-1',
                    u'utf8:portal_type': u'utf8:opengever.inbox.forwarding',
                    u'utf8:title': u'utf8:Ein Testdokument'}}
)

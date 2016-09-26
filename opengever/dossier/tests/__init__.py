from datetime import datetime
from plone.app.testing import TEST_USER_ID


EXPECTED_USER_DOC_PROPERTIES = {
    'User.ID': TEST_USER_ID,
    'User.FullName': u'M\xfcller Peter',
    'ogg.user.userid': TEST_USER_ID,
    'ogg.user.title': u'M\xfcller Peter',
    'ogg.user.firstname': u'Peter',
    'ogg.user.lastname': u'M\xfcller',
    'ogg.user.directorate': u'Staatsarchiv',
    'ogg.user.directorate_abbr': u'Arch',
    'ogg.user.department': u'Staatskanzlei',
    'ogg.user.department_abbr': u'SK',
    'ogg.user.email': u'foo@example.com',
    'ogg.user.email2': u'bar@example.com',
    'ogg.user.url': u'http://www.example.com',
    'ogg.user.phone_office': u'012 34 56 78',
    'ogg.user.phone_fax': u'012 34 56 77',
    'ogg.user.phone_mobile': u'012 34 56 76',
    'ogg.user.salutation': u'Prof. Dr.',
    'ogg.user.description': u'nix',
    'ogg.user.address1': u'Kappelenweg 13',
    'ogg.user.address2': u'Postfach 1234',
    'ogg.user.zip_code': u'1234',
    'ogg.user.city': u'Vorkappelen',
    'ogg.user.country': u'Schweiz',
}

OGDS_USER_ATTRIBUTES = {
    'firstname': u'Peter',
    'lastname': u'M\xfcller',
    'directorate': u'Staatsarchiv',
    'directorate_abbr': u'Arch',
    'department': u'Staatskanzlei',
    'department_abbr': u'SK',
    'email': u'foo@example.com',
    'email2': u'bar@example.com',
    'url': u'http://www.example.com',
    'phone_office': u'012 34 56 78',
    'phone_fax': u'012 34 56 77',
    'phone_mobile': u'012 34 56 76',
    'salutation': u'Prof. Dr.',
    'description': u'nix',
    'address1': u'Kappelenweg 13',
    'address2': u'Postfach 1234',
    'zip_code': u'1234',
    'city': u'Vorkappelen',
    'country': u'Schweiz',
}

EXPECTED_DOSSIER_PROPERTIES = {
    'Dossier.ReferenceNumber': 'Client1 / 1',
    'Dossier.Title': 'My dossier',
    'ogg.dossier.title': 'My dossier',
    'ogg.dossier.reference_number': 'Client1 / 1',
    'ogg.dossier.sequence_number': '1',
}

EXPECTED_DOCUMENT_PROPERTIES = {
    'Document.ReferenceNumber': 'Client1 / 1 / 1',
    'Document.SequenceNumber': '1',
    'ogg.document.title': "My Document",
    'ogg.document.reference_number': 'Client1 / 1 / 1',
    'ogg.document.sequence_number': '1',
    'ogg.document.document_author': u'M\xfcller Peter',
    'ogg.document.document_date': datetime(2010, 1, 3),
    'ogg.document.reception_date': datetime(2010, 1, 3),
    'ogg.document.delivery_date': datetime(2010, 1, 3),
}


EXPECTED_DOC_PROPERTIES = dict(
    EXPECTED_USER_DOC_PROPERTIES.items() +
    EXPECTED_DOSSIER_PROPERTIES.items() +
    EXPECTED_DOCUMENT_PROPERTIES.items()
)

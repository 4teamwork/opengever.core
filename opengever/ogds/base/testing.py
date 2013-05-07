from plone.dexterity import utils


def create_contacts(portal):
    """Creates a bunch of contacts for testing with.
    """
    # create contact folder
    if 'contacts' not in portal.objectIds():
        contacts = utils.createContentInContainer(
            portal,
            'opengever.contact.contactfolder',
            checkConstraints=False,
            title='Contacts')
        assert 'contacts' in portal.objectIds(), \
            'Could not create contacts folder'
        contacts.reindexObject()
    else:
        contacts = portal.contacts

    contact_list = (
        ('Sandra', 'Kaufmann', 'sandra.kaufmann@test.ch'),
        ('Elisabeth', u'K\xe4ppeli'.encode('utf8'),
         'elisabeth.kaeppeli@test.ch'),
        ('Roger', 'Wermuth', None))

    for firstname, lastname, email in contact_list:
        obj = utils.createContentInContainer(
            contacts,
            'opengever.contact.contact',
            checkConstraints=False,
            firstname=firstname.decode('utf-8'),
            lastname=lastname.decode('utf-8'),
            email=email)
        obj.reindexObject()

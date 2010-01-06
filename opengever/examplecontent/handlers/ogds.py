

from opengever.examplecontent.handlers.utils import TypeGenerator
from opengever.examplecontent.handlers.utils import ContactGenerator
from opengever.examplecontent.handlers.utils import createContentInContainer

class SetupVarious(object):

    def __call__(self, setup):
        self.setup = setup
        self.portal = self.setup.getSite()
        self.openDataFile = self.setup.openDataFile
        self.setup_clients()
        self.setup_contacts()

    def setup_clients(self):
        print '---- setting up clients ----'
        gen = TypeGenerator(self.setup)
        type = 'ftw.directoryservice.client'
        data = self.openDataFile('clients.csv')
        self.clients = list(gen.create_from_csv(container=self.portal,
                                                portal_type=type,
                                                csv_stream=data,
                                                checkConstraints=True,
                                                skip_existing_identified_by='title'))

    def setup_contacts(self):
        print '---- adding contacts ----'
        type = 'ftw.directoryservice.contact'
        self.contacts = []
        gen = ContactGenerator(self.setup)
        contact_data = list(gen.list_contact_data())
        contacts_per_client = len(contact_data) / len(self.clients)
        for c, client in enumerate(self.clients):
            start = c * contacts_per_client
            end = start + contacts_per_client
            end = end<=len(contact_data) and end or len(contact_data)
            for data in contact_data[start:end]:
                if c!=0:
                    del data['userid']
                obj = createContentInContainer(container=client,
                                               portal_type=type,
                                               checkConstraints=True,
                                               **data)
                print '** created contact %s %s' % (
                    data['firstname'],
                    data['lastname'],
                    )
                self.contacts.append(obj)

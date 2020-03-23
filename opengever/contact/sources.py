from opengever.contact.models import Contact
from opengever.contact.models import Organization
from opengever.contact.models import OrgRole
from opengever.contact.models import Person
from opengever.contact.ogdsuser import OgdsUserToContactAdapter
from opengever.ogds.models.service import ogds_service
from z3c.formwidget.query.interfaces import IQuerySource
from zope.interface import implementer
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm


@implementer(IQuerySource)
class ContactsSource(object):
    """A source of all active contacts (all persons and organizations).
    """

    by_type = {'person': Person,
               'organization': Organization,
               'org_role': OrgRole,
               'ogds_user': OgdsUserToContactAdapter}
    by_class = {v: k for k, v in by_type.iteritems()}

    def __init__(self, context):
        self.context = context
        self.terms = []

    def __contains__(self, value):
        """Currently all Contacts and OrgRoles are considered valid.
        """
        return value.__class__ in self.by_class

    def __iter__(self):
        return self.terms.__iter__()

    def __len__(self):
        return len(self.terms)

    def getTerm(self, value):
        term_type = self.by_class[value.__class__]
        return SimpleTerm(value=value,
                          token='{}:{}'.format(term_type, value.id),
                          title=value.get_title(with_former_id=True))

    def getTermByToken(self, token):
        if not token:
            raise LookupError

        term_type, term_id = token.split(':')
        term_id = term_id
        clazz = self.by_type[term_type]
        contact = clazz.query.get(term_id)
        if not contact:
            raise LookupError
        return self.getTerm(contact)

    def search(self, query_string):
        self.terms = []

        text_filters = query_string.split()
        query = Contact.query.filter(Contact.is_active == True)  # noqa
        query = query.polymorphic_by_searchable_text(
            text_filters=text_filters)

        for contact in query.order_by(Contact.contact_id):
            self.terms.append(self.getTerm(contact))
            if hasattr(contact, 'organizations'):
                for org_role in contact.organizations:
                    self.terms.append(self.getTerm(org_role))

        for ogds_user in ogds_service().filter_users(text_filters):
            self.terms.append(
                self.getTerm(OgdsUserToContactAdapter(ogds_user)))

        return self.terms


@implementer(IContextSourceBinder)
class ContactsSourceBinder(object):
    """A vocabulary factory for the ContactsVocabulary.
    """

    implements(IVocabularyFactory)

    def __call__(self, context):
        return ContactsSource(context)

from collective.elephantvocabulary import wrap_vocabulary
from five import grok
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.vocabularies import generator_to_list
from opengever.ogds.base.vocabularies import voc_cachekey
from opengever.ogds.base.vocabulary import ContactsVocabulary
from plone.memoize import ram
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
import AccessControl


# XXX move to ogds
class AllUsersAndInboxesVocabularyFactory(grok.GlobalUtility):
    """Vocabulary of all users and all inbexes, but client unspecific.
    The client is added as prefix to each user.
    Users assigned to multiple clients are once per client in the vocabulary.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.AllUsersAndInboxesVocabulary')

    hidden_terms = []

    def __call__(self, context):
        self.context = context
        vocab = wrap_vocabulary(
            ContactsVocabulary.create_with_provider(
                self.key_value_provider))(context)
        vocab.hidden_terms = self.hidden_terms
        return vocab

    @ram.cache(voc_cachekey)
    @generator_to_list
    def key_value_provider(self):
        info = getUtility(IContactInformation)

        for client in info.get_clients():
            client_id = client.client_id

            # all users
            for user in info.list_assigned_users(client_id=client_id):
                value = u'%s:%s' % (client_id, user.userid)
                label = u'%s: %s' % (
                    client.title,
                    info.describe(user))

                if not user.active:
                    self.hidden_terms.append(value)

                yield (value, label)

            # client inbox
            principal = u'inbox:%s' % client_id
            value = u'%s:%s' % (client_id, principal)
            label = info.describe(principal)
            yield (value, label)


@grok.provider(IContextSourceBinder)
def attachable_documents_vocabulary(context):
    terms = []

    user = AccessControl.getSecurityManager().getUser()
    if user == AccessControl.SpecialUsers.nobody:
        return SimpleVocabulary(terms)

    intids = getUtility(IIntIds)

    for doc in context.getFolderContents(
        full_objects=True,
        contentFilter={'portal_type': ['opengever.document.document',
                                       'ftw.mail.mail']}):

        key = str(intids.getId(doc))
        label = doc.Title()
        terms.append(SimpleVocabulary.createTerm(key, key, label))

    for relation in getattr(context, 'relatedItems', []):
        key = str(relation.to_id)
        label = relation.to_object.Title()
        terms.append(SimpleVocabulary.createTerm(key, key, label))

    return SimpleVocabulary(terms)

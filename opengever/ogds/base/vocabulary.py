from five import grok
from z3c.formwidget.query.interfaces import IQuerySource
from zope.schema.vocabulary import SimpleVocabulary


class ContactsVocabulary(SimpleVocabulary):

    grok.implements(IQuerySource)

    def search(self, query_string):
        """search method for `z3c.formwidget.autocomplete` support. Returns
        all matching contacts.
        """

        query_string = isinstance(query_string, str) and \
            query_string.decode('utf8') or query_string
        query = query_string.lower().split(' ')
        for i, word in enumerate(query):
            query[i] = word.strip()

        if not self.provider and len(self) > 0:
            for v in self:
                if self._compare(query, v.value):
                    yield v

        elif self.provider:
            items = list(self.provider())
            for key, value in items:
                if self._compare(query, value):
                    yield self.__class__.createTerm(key, key, value)

    def _compare(self, query, value):
        """ Compares each word in the query string seperate.

        Example 1:
        Given value: Hugo Boss
        Query "hu bo" matches
        Query "bo hu" matches
        Query "boh" doesnt match (its not fuzzy matching yet)
        Query "hub" doesnt match

        Example 2:
        Given value: Eingangskorb Mandant 1
        Query "m 1" matches
        Query "m 1 eing" matches
        Query "m1" doesnt match
        """

        if not value:
            return False
        value = isinstance(value, str) and \
            value.decode('utf8').lower() or value.lower()
        for word in query:
            if len(word) > 0 and word not in value:
                return False
        return True

    @property
    def provider(self):
        """Returns the source provider of this vocabulary instance.
        See also the factories in `contacts.py`.
        """

        return getattr(self, '_provider', None)

    @classmethod
    def get_terms_from_provider(cls, provider):
        """Return all terms of a specfic provider.
        """

        terms = []
        termed_keys = set()
        for key, label in provider():
            if key not in termed_keys:
                termed_keys.add(key)

                if isinstance(label, str):
                    label = label.decode('utf8')
                terms.append(cls.createTerm(
                        key, key.encode('ascii', 'replace'), label))

        return terms

    @classmethod
    def create_with_provider(cls, provider):
        """Creates a new vocabulary instance and fills it with terms from the
        given `provider`.
        """

        voc = cls(cls.get_terms_from_provider(provider))
        voc._provider = provider
        return voc

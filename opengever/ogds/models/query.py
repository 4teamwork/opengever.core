from sqlalchemy import or_
from sqlalchemy import String
from sqlalchemy.orm import Query
from sqlalchemy.orm.base import _entity_descriptor
from sqlalchemy.sql.expression import cast


class BaseQuery(Query):

    searchable_fields = []

    def _attribute(self, name):
        """ Return keyword expressions extracted from the primary
        entity of the query, or the last entity that was the
        target of a call to `.Query.join`.

        """
        return _entity_descriptor(self._joinpoint_zero(), name)

    def by_searchable_text(self, text_filters=[]):
        """Extends the given `query` with text_filters, a list of text snippets.
        """
        fields = [self._attribute(f) for f in self.searchable_fields]
        return extend_query_with_textfilter(self, fields, text_filters)


def extend_query_with_textfilter(query, fields, text_filters):
    if text_filters:
        for word in text_filters:
            term = _add_wildcards(word)

            expressions = []
            for field in fields:
                if not issubclass(field.type.python_type, basestring):
                    field = cast(field, String)
                expressions.append(field.ilike(term))

            query = query.filter(or_(*expressions))

    return query


def _add_wildcards(word):
    """Add leading and trailing wildcards and replace asterisks with
    wildcards.
    """

    word = word.strip('*').replace('*', '%')
    return u'%{0}%'.format(word)

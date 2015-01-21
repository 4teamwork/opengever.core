from five import grok
from ftw.dictstorage.interfaces import ISQLAlchemy
from opengever.base.behaviors.classification import translated_public_trial_terms
from opengever.base.interfaces import IReferenceNumberFormatter
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.ogds.base.sort_helpers import SortHelpers
from opengever.tabbedview.browser.listing import ListingView
from opengever.tabbedview.browser.sqltablelisting import SqlTableSource
from opengever.tabbedview.utils import get_translated_transitions
from opengever.tabbedview.utils import get_translated_types
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import queryAdapter
from zope.interface import implements
from zope.interface import Interface
import re


class OpengeverTab(object):
    implements(ISQLAlchemy)

    show_searchform = True

    def get_css_classes(self):
        if self.show_searchform:
            return ['searchform-visible']
        else:
            return ['searchform-hidden']

    # XXX : will be moved to registry later...
    extjs_enabled = True

    # XXX: this method contains sorting stuff that applies to tasks only.
    def custom_sort(self, results, sort_on, sort_reverse):
        """We need to handle some sorting for special columns, which are
        not sortable in the catalog...
        """
        if getattr(self, '_custom_sort_method', None) is not None:
            results = self._custom_sort_method(results, sort_on, sort_reverse)

        elif sort_on == 'sequence_number':
            splitter = re.compile('[/\., ]')

            def _sortable_data(brain):
                """ Converts the "reference" into a tuple containing integers,
                which are converted well. Sorting "10" and "2" as strings
                results in wrong order..
                """

                value = getattr(brain, sort_on, '')
                if not isinstance(value, str) and not isinstance(
                    value, unicode):
                    return value
                parts = []
                for part in splitter.split(value):
                    part = part.strip()
                    try:
                        part = int(part)
                    except ValueError:
                        pass
                    parts.append(part)
                return parts
            results = list(results)
            results.sort(
                lambda a, b: cmp(_sortable_data(a), _sortable_data(b)))
            if sort_reverse:
                results.reverse()

        elif sort_on == 'reference':
            # Get active reference formatter
            registry = getUtility(IRegistry)
            proxy = registry.forInterface(IReferenceNumberSettings)
            formatter = queryAdapter(IReferenceNumberFormatter,
                                     name=proxy.formatter)
            results = list(results)
            results.sort(key=formatter.sorter)
            if sort_reverse:
                results.reverse()

        # custom sort for sorting on the readable fullname
        # of the users, contacts and inboxes
        elif sort_on in (
            'responsible', 'Creator', 'checked_out', 'issuer', 'contact'):

            if sort_on in ('issuer', 'contact'):
                sort_dict = SortHelpers().get_user_contact_sort_dict()
            else:
                sort_dict = SortHelpers().get_user_sort_dict()

            def _sorter(a, b):
                return cmp(
                    sort_dict.get(
                        getattr(a, sort_on, ''), getattr(a, sort_on, '')),
                    sort_dict.get(
                        getattr(b, sort_on, ''), getattr(b, sort_on, ''))
                    )

            results = list(results)
            results.sort(_sorter, reverse=sort_reverse)

        elif sort_on == 'review_state':
            states = get_translated_transitions(self.context, self.request)

            def _state_sorter(a, b):
                return cmp(
                    states.get(
                        getattr(a, sort_on, ''), getattr(a, sort_on, '')),
                    states.get(
                        getattr(b, sort_on, ''), getattr(b, sort_on, ''))
                    )

            results = list(results)
            results.sort(_state_sorter, reverse=sort_reverse)

        elif sort_on == 'task_type':
            types = get_translated_types(self.context, self.request)

            def _type_sorter(a, b):

                return cmp(
                    types.get(
                        getattr(a, sort_on, ''), getattr(a, sort_on, '')),
                    types.get(getattr(b, sort_on, ''), getattr(b, sort_on, ''))
                    )

            results = list(results)
            results.sort(_type_sorter, reverse=sort_reverse)

        elif sort_on == 'public_trial':
            values = translated_public_trial_terms(self.context, self.request)

            def _public_trial_sorter(a, b):
                return cmp(
                    values.get(
                        getattr(a, sort_on, ''), getattr(a, sort_on, '')),
                    values.get(getattr(b, sort_on, ''), getattr(b, sort_on, ''))
                    )

            results = list(results)
            results.sort(_public_trial_sorter, reverse=sort_reverse)

        return results


class BaseListingTab(grok.View, OpengeverTab, ListingView):
    """Base listing tab."""

    grok.context(Interface)
    grok.require('zope2.View')

    sort_on = 'modified'
    sort_reverse = False
    #lazy must be false otherwise there will be no correct batching
    lazy = False

    # the model attributes is used for a dynamic textfiltering functionality
    enabled_actions = []
    major_actions = []

    model = None

    # seems like grok cannot inherit these:
    __call__ = ListingView.__call__
    update = ListingView.update
    render = __call__


class BaseTableSource(SqlTableSource):

    grok.baseclass()

    def build_query(self):
        """Builds the query based on `get_base_query()` method of config.
        Returns the query object.
        """
        # initalize config
        self.config.update_config()

        # get the base query from the config
        query = self.config.get_base_query()
        query = self.validate_base_query(query)

        return query

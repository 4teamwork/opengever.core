from functools import partial
from plone import api
from plone.supermodel.interfaces import IDefaultFactory
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.Expression import Expression
from Products.CMFPlone.utils import safe_unicode
from zope.globalrequest import getRequest
from zope.interface import directlyProvides
import logging


logger = logging.getLogger('opengever.propertysheets')


def attach_expression_default_factory(field, default_expression):
    """Set a defaultFactory on a field to dynamically evaluate default_expression
    """
    factory = partial(tales_expr_default_factory, default_expression)

    # Because PropertySheet widgets currently are not context aware,
    # this is not a context aware factory.
    directlyProvides(factory, IDefaultFactory)

    field.defaultFactory = factory


def tales_expr_default_factory(expression):
    result = None

    # We need to be very defensive here. Evaluating an unwisely constructed
    # expression can raise all sorts of nasty exceptions, including
    # Unauthorized, KeyError, LocationError, ... that would wreck page
    # rendering (or API responses). This is especially true since
    # defaultFactories also may get invoked for widgets in display mode.
    try:
        portal = api.portal.get()
        if not portal:
            return None

        # PropertySheet z3c.form widgets are currently not context aware.
        # We therefore don't pass a context as the `object` argument.
        #
        # But because createExprContext() unconditionally tries to get
        # folder.absolute_url(), we need to provide it with *some* kind
        # of object. `folder` therefore gets set to the portal as well.
        ec = createExprContext(folder=portal, portal=portal, object=None)
        expr = Expression(expression)
        result = expr(ec)

        if isinstance(result, str):
            # Most text-like zope.schema fields require unicode
            result = safe_unicode(result)

    except Exception as exc:
        logger.warn(
            'Failed to evaluate TALES expression %r for request %r: '
            'Got: %r' % (expression, getRequest(), exc))

    return result

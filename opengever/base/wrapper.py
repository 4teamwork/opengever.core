from Acquisition import Implicit
from OFS.Traversable import Traversable
from opengever.base.interfaces import ISQLObjectWrapper
from zope.interface import implements
import ExtensionClass


class SQLWrapperBase(ExtensionClass.Base, Implicit, Traversable):
    """SQL objects Wrapper class to fake a context.
    """

    implements(ISQLObjectWrapper)

    default_view = 'view'

    def __init__(self, context, model):
        self.parent = context
        self.model = model

    @classmethod
    def wrap(cls, context, model):
        wrapper = cls(context, model)
        return wrapper.__of__(context)

    def absolute_url(self):
        return self.model.get_url(view=None)

    def get_breadcrumb(self):
        return {'absolute_url': self.absolute_url(),
                'title': self.get_title(),
                'css_class': getattr(self.model, 'css_class', '')}

    def get_title(self):
        return self.model.get_title()

    def __before_publishing_traverse__(self, arg1, arg2=None):
        """Implements default-view behavior for sql wrapper objects.

        Means that if a sql wrapper gets accessed directly without a view,
        the pre-traversal hook make sure that a default view gets displayed,
        except when we are trying to access a REST-API service.
        """
        # XXX hack around a bug(?) in BeforeTraverse.MultiHook
        # see Products.CMFCore.DynamicType.__before_publishing_traverse__
        REQUEST = arg2 or arg1

        stack = REQUEST['TraversalRequestNameStack']

        if stack == [] and not getattr(REQUEST, '_rest_service_id', None) == 'GET_application_json_':
            stack.append(self.default_view)
            REQUEST._hacked_path = 1

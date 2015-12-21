from Acquisition import Implicit
from OFS.Traversable import Traversable
from opengever.locking.interfaces import ISQLLockable
from opengever.meeting.interfaces import IMeetingWrapper
from opengever.meeting.interfaces import IMemberWrapper
from opengever.meeting.interfaces import IMembershipWrapper
from opengever.meeting.model import Membership
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
from zope.interface import implements
import ExtensionClass


class BaseWrapper(ExtensionClass.Base, Implicit, Traversable):

    implements(IHideFromBreadcrumbs)

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

    def get_breadcrumbs(self):
        return ({'absolute_url': self.absolute_url(),
                 'Title': self.get_title()},)

    def get_title(self):
        return self.model.get_title()

    def __before_publishing_traverse__(self, arg1, arg2=None):
        """Implements default-view behavior for meetings.

        Means that if a meeting gets accessed directly without a view,
        the pre-traversal hook make sure that a default view gets displayed.
        """

        # XXX hack around a bug(?) in BeforeTraverse.MultiHook
        # see Products.CMFCore.DynamicType.__before_publishing_traverse__
        REQUEST = arg2 or arg1

        stack = REQUEST['TraversalRequestNameStack']
        if stack == []:
            stack.append(self.default_view)
            REQUEST._hacked_path = 1


class MeetingWrapper(BaseWrapper):

    implements(IMeetingWrapper, ISQLLockable)


class MemberWrapper(BaseWrapper):

    implements(IMemberWrapper)

    def absolute_url(self):
        return self.model.get_url(self.parent)

    def get_title(self):
        return self.model.fullname

    def __getitem__(self, key):
        if not key.startswith('membership'):
            raise KeyError(key)

        membership_id = int(key.split('-')[-1])
        membership = Membership.query.get(membership_id)
        if not membership:
            raise KeyError(key)

        return MembershipWrapper.wrap(self, membership)


class MembershipWrapper(BaseWrapper):

    implements(IMembershipWrapper)

    default_view = 'edit'

    def absolute_url(self):
        return self.model.get_url(self.parent)

    def get_title(self):
        return u'{}, {} - {}'.format(self.model.title(),
                                     self.model.format_date_from(),
                                     self.model.format_date_to())

    def get_breadcrumbs(self):
        my_breadcrumbs = super(MembershipWrapper, self).get_breadcrumbs()
        parent_breadcrumbs = self.parent.get_breadcrumbs()
        return parent_breadcrumbs + my_breadcrumbs

from Acquisition import aq_inner
from opengever.base import _
from plone import api
from plone.protect import CheckAuthenticator
from plone.protect import protect
from Products.CMFPlone import PloneMessageFactory as pmf
from Products.Five import BrowserView
from zc.relation.interfaces import ICatalog
from zExceptions import Forbidden
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission


class FolderDeleteConfirmation(BrowserView):

    def __init__(self, context, request):
        super(FolderDeleteConfirmation, self).__init__(context, request)
        self.portal = api.portal.get()
        self.ref_catalog = getUtility(ICatalog)
        self.intids = getUtility(IIntIds)

        self.objs_without_backrefs = None
        self.objs_with_backrefs = None

    def __call__(self):
        objs = self._lookup_objects_by_path(self.request.form.get('paths', []))

        # Redirects to the original template if the user aborted the confirmation.
        if 'form.button.Cancel' in self.request.form:
            return self._redirect_to_orig_template()

        # Check if one or more objects are selected
        if not objs:
            api.portal.show_message(pmf(u'Please select one or more items to delete.'), self.request, type="error")
            return self._redirect_to_orig_template()

        # Split the given objects into objects with backrefs and objects without backrefs
        self.objs_without_backrefs, self.objs_with_backrefs = self._check_backreferences_for_objs(objs)

        # Delete the given objects
        if 'form.submitted' in self.request.form:
            try:
                return self._handle_form_submitted(self.request)
            except Forbidden:
                return self._redirect_to_orig_template()

        # Returns a confirmation-template
        return super(FolderDeleteConfirmation, self).__call__()

    @protect(CheckAuthenticator)
    def _handle_form_submitted(self, REQUEST=None):
        self._delete_objs(self.objs_without_backrefs)
        api.portal.show_message(pmf(u'Items successfully deleted.'),
                                self.request, type="info")
        return self._redirect_to_orig_template()

    def _delete_objs(self, objs):
        """Deletes all the given objects
        """
        if not objs:
            return
        api.content.delete(objects=objs)

    def _redirect_to_orig_template(self):
        """Redirects to the original template
        """
        return self.context.REQUEST.RESPONSE.redirect(
            self.request.form.get('orig_template', self.context.absolute_url()))

    def _lookup_object_by_path(self, path):
        """Lookusup the obj by the given path.

        Returns None if the object does not exists.
        """
        return self.portal.restrictedTraverse(path, None)

    def _lookup_objects_by_path(self, paths):
        """Lookup all objects for the given paths.

        The function will return only existing objects.
        The function wont raise an error if there is an invalid path.
        """
        return filter(lambda x: x is not None,
                      [self._lookup_object_by_path(path) for path in paths])

    def _check_backreferences_for_objs(self, objs):
        """Returns a two lists.

        - The first list contains all objects without backreferences
        - The second list contains all objects with backreferences.

        The list with backreferences contains tuples with the obj as the first
        element and the backrefs as the second element.

        i.e. [(obj1, [bref1, bref2]), (obj2, [bref3])]
        """
        objs_with_backrefs = []
        objs_without_backrefs = []
        for obj in objs:
            backrefs = self._get_backrefs_for_obj(obj)
            if backrefs:
                objs_with_backrefs.append((obj, backrefs))
            else:
                objs_without_backrefs.append(obj)

        return objs_without_backrefs, objs_with_backrefs

    def _get_backrefs_for_obj(self, obj):
        """Returns all backreferences as BackReference objects of an object in a list.
        """
        backrefs = []
        intid = self.intids.getId(aq_inner(obj))
        for rel in self.ref_catalog.findRelations({'to_id': intid}):
            obj = rel.from_object
            if obj is None:
                continue

            if checkPermission('zope2.View', obj):
                backrefs.append(BackReference(obj.pretty_title_or_id(), obj.absolute_url()))
            else:
                backrefs.append(UnauthorizedBackReference())

        return backrefs


class BackReference(object):
    title = ''
    url = ''

    def __init__(self, title, url):
        self.title = title
        self.url = url

    def get_html_link(self):
        if self.url:
            return '<a href="{}">{}</a>'.format(self.url, self.title)
        return self.title


class UnauthorizedBackReference(BackReference):
    def __init__(self, title=None, url=None):
        self.title = _('unauthorized_backreference',
                       default="You are not allowed to see this reference")

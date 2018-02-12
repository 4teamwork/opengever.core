from AccessControl import getSecurityManager
from Acquisition import aq_chain
from BTrees.OOBTree import OOBTree
from opengever.base.protect import unprotected_write
from opengever.portlets.tree.interfaces import IRepositoryFavorites
from opengever.repository.repositoryroot import IRepositoryRoot
from persistent.list import PersistentList
from plone import api
from plone.app.caching.interfaces import IETagValue
from Products.Five import BrowserView
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface
import json
import md5


ANNOTATION_KEY = 'og-treeportlet-favorites'


def to_unicode(item):
    if isinstance(item, str):
        return item.decode('utf-8')
    elif isinstance(item, unicode):
        return item
    else:
        return unicode(item)


class RepositoryFavorites(object):
    implements(IRepositoryFavorites)
    adapts(IRepositoryRoot, Interface)

    def __init__(self, repositoryroot, username):
        self.context = repositoryroot
        self.username = username

    def add(self, uuid):
        uuid = to_unicode(uuid)
        if uuid not in self.annotations:
            self.annotations.append(uuid)

    def remove(self, uuid):
        uuid = to_unicode(uuid)
        if uuid in self.annotations:
            self.annotations.remove(uuid)

    def list(self):
        return list(self.annotations)

    def set(self, uuids):
        self.annotations[:] = map(to_unicode, uuids)

    @property
    def annotations(self):
        annotations = unprotected_write(IAnnotations(self.context))
        if ANNOTATION_KEY not in annotations:
            annotations[ANNOTATION_KEY] = OOBTree()

        unprotected_write(annotations[ANNOTATION_KEY])
        if self.username not in annotations[ANNOTATION_KEY]:
            annotations[ANNOTATION_KEY][self.username] = PersistentList()

        return unprotected_write(annotations[ANNOTATION_KEY][self.username])


class RepositoryFavoritesView(BrowserView):

    def list(self):
        """Returns a JSON list of favorites uuids for current user and context.
        """
        response = self.request.response
        response.setHeader('Content-Type', 'application/json')
        response.setHeader('X-Theme-Disabled', 'True')
        response.enableHTTPCompression(REQUEST=self.request)

        if self.request.get('cache_key'):
            # Only cache when there is a cache_key in the request.
            # The cached representation is to be considered fresh for 1 year
            # http://stackoverflow.com/a/3001556/880628
            response.setHeader('Cache-Control', 'private, max-age=31536000')

        return json.dumps(self._storage().list())

    def add(self):
        """Adds a new uuid to the favorites.
        """
        uuid = self.request.get('uuid')
        if not uuid or not isinstance(uuid, (str, unicode)):
            raise ValueError('Invalid uuid: {0}'.format(uuid))
        self._storage().add(uuid)

    def remove(self):
        """Removes a uuid from the favorites.
        """
        uuid = self.request.get('uuid')
        if not uuid or not isinstance(uuid, (str, unicode)):
            raise ValueError('Invalid uuid: {0}'.format(uuid))
        self._storage().remove(uuid)

    def set(self):
        """Sets a new list of favorite uuids.
        """
        uuids = self.request.get('uuids[]')
        if not uuids or not isinstance(uuids, list):
            raise ValueError('Invalid list of uuids: {0}'.format(uuids))
        for item in uuids:
            if not isinstance(item, (str, unicode)):
                raise ValueError('Invalid uuid: {0}; {1}'.format(item, uuids))
        self._storage().set(uuids)

    def list_cache_param(self):
        username = getSecurityManager().getUser().getId()
        cache_key = '-'.join((self.get_cache_key(), username))
        param = 'cache_key={0}'.format(cache_key)
        if self.request.getHeader('Cache-Control') == 'no-cache':
            param += '&nocache=true'
        return param

    def get_cache_key(self):
        cache_key_data = ':'.join(self._storage().list())
        return md5.new(cache_key_data).hexdigest()

    def _storage(self):
        username = getSecurityManager().getUser().getId()
        return getMultiAdapter((self.context, username), IRepositoryFavorites)


@implementer(IETagValue)
@adapter(Interface, Interface)
class RepositoryFavoritesETagValue(object):

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def __call__(self):
        return '-'.join(map(self.get_cache_key_for_repository_root,
                            self.get_repository_roots()))

    def get_cache_key_for_repository_root(self, repository_root):
        if api.user.is_anonymous():
            # Anonymous users can't have repository favorites - short circuit
            # cache key generation, no need to ask the view
            return ''
        view = repository_root.restrictedTraverse('repository-favorites')
        return view.get_cache_key()

    def get_repository_roots(self):
        roots = filter(IRepositoryRoot.providedBy, aq_chain(self.published))
        if roots:
            return roots
        # Avoid catalog query for performance reasons
        return filter(IRepositoryRoot.providedBy, getSite().objectValues())

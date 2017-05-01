from Products.Five import BrowserView
from zExceptions import Unauthorized


class TraversalUnauthorized(BrowserView):

    def __init__(self, context, request):
        raise Unauthorized()


class PublishingUnauthorized(BrowserView):

    def __call__(self):
        raise Unauthorized()

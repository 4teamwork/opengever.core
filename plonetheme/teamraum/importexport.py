from BTrees.OOBTree import OOBTree
from plone.app.blob.field import BlobWrapper, ReuseBlob
from plone.app.blob.interfaces import IBlobbable
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from zope.annotation.interfaces import IAnnotations
import base64
import copy
import json


LOGO_KEY = 'css.logo'
LOGO_RIGHT_KEY = 'css.logo_right'
LOGO_TITLE_KEY = 'css.logo_title'
CSS_PREFIX = 'css.'

DEFAULT_STYLES = {
    'css.gnav_shadowtop': '#4c565f',
    'css.gnav_shadowinset': '#017ed8',
    'css.gnav_grad_start': '#00528d',
    'css.gnav_grad_end': '#03253d',
    'css.gnav_hover_start': '#005fa2',
    'css.gnav_hover_end': '#004373',
    'css.gnav_hover_shadowtop': '#3e464c',
    'css.gnav_hover_shadowinset': '#0077cc',
    'css.gnav_active_start': '#002947',
    'css.gnav_active_end': '#00192a',
    'css.gnav_active_shadowtop': '#265070',
    'css.gnav_active_shadowinset': '#003559',
    'css.header_background': '#FFFFFF',
    'css.header_height': '60px',
    'css.headerbox_spacetop': '1em',
    'css.show_headerbox': '',
    'css.show_fullbanner': '',
    'css.logo_spaceleft': 'true',
    'css.headerbox_background': 'rgba(255,255,255,0.6)',
    'css.content_background': '#FFFFFF',
    'css.content_width': '1000px',
    'css.link_color': '#205C90',
    'css.text_color': '#444',
    'css.footer_background': '#f8f8f8',
    'css.footer_height': '10',
    'css.font_size': '12px',
    'css.login_background': '#006bb8',
    'show_logo_on_the_right': 'false'
#    'css.logo': '',
    }


class CustomStylesUtility(object):
    """This utility is in charge of handling import and export of custom
    styles. It is used by the setuphandlers and the controlpanel.
    """

    def __init__(self, context):
        self.context = context

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    @property
    def annotations(self):
        return IAnnotations(self.portal)

    @property
    def portal_css(self):
        return getToolByName(self.context, 'portal_css')

    @property
    def defaults(self):
        return self.annotations.get('customstyles', OOBTree(DEFAULT_STYLES))

    def reset_styles(self):
        """Reset the custom styles to defaults.
        """
        self.annotations['customstyles'] = OOBTree(DEFAULT_STYLES)

    def reset_logo_right(self):
        """Reset the custom styles logo on the right side.
        """
        if LOGO_RIGHT_KEY in self.annotations['customstyles']:
            del self.annotations['customstyles'][LOGO_RIGHT_KEY]
            #TODO: save_styles to recalculate the logo padding...

    def reset_logo(self):
        """Reset the custom styles logo.
        """
        if LOGO_KEY in self.annotations['customstyles']:
            del self.annotations['customstyles'][LOGO_KEY]
            #TODO: save_styles to recalculate the logo padding...

    def get_logo_right(self, logo_file):
        """ Read the logo from a file-like stream object `logo_file` and create
        a blob from it, or resuse the existing one if none has been uploaded.
        """
        logo, blob = None, None
        data = logo_file.read()
        if data:
            blob = BlobWrapper('image/png')
            if isinstance(data, basestring):
                value = StringIO(data)
                if value is not None:
                    blobbable = IBlobbable(value)
                    try:
                        blobbable.feed(blob.getBlob())
                    except ReuseBlob, exception:
                        blob.setBlob(exception.args[0])
            blob.setFilename(blobbable.filename())
        if blob:
            logo = blob
        elif LOGO_RIGHT_KEY in self.annotations['customstyles']:
            # use existing logo if none is uploaded
            logo = self.annotations['customstyles'][LOGO_RIGHT_KEY]
        return logo

    def get_logo(self, logo_file):
        """ Read the logo from a file-like stream object `logo_file` and create
        a blob from it, or resuse the existing one if none has been uploaded.
        """
        logo, blob = None, None
        data = logo_file.read()
        if data:
            blob = BlobWrapper('image/png')
            if isinstance(data, basestring):
                value = StringIO(data)
                if value is not None:
                    blobbable = IBlobbable(value)
                    try:
                        blobbable.feed(blob.getBlob())
                    except ReuseBlob, exception:
                        blob.setBlob(exception.args[0])
            blob.setFilename(blobbable.filename())
        if blob:
            logo = blob
        elif LOGO_KEY in self.annotations['customstyles']:
            # use existing logo if none is uploaded
            logo = self.annotations['customstyles'][LOGO_KEY]
        return logo

    def save_styles(self, items):
        """Saves the styles passed in as items to annotations.
        """
        styles = {}
        for key, value in items.items():
            if key == LOGO_KEY:
                logo = self.get_logo(value)
                styles[LOGO_KEY] = logo
            elif key == LOGO_RIGHT_KEY:
                logo_right = self.get_logo_right(value)
                styles[LOGO_RIGHT_KEY] = logo_right
            elif key == LOGO_TITLE_KEY:
                if isinstance(value, unicode):
                    value = value.encode('utf8')
                styles[key] = value.decode('utf8')
            elif key.startswith(CSS_PREFIX):
                styles[key] = value

        self.annotations['customstyles'] = OOBTree(styles)
        # TODO: save theme settings
        # applyTheme(None)
        self.portal_css.cookResources()

    def export_styles(self):
        """Returns a json file containing the styles.
        """
        styles = copy.deepcopy(self.annotations['customstyles'])

        if LOGO_KEY in styles:
            # copy blob directly from annotations
            styles[LOGO_KEY] = base64.b64encode(
                self.annotations['customstyles'][LOGO_KEY].data)

        if LOGO_RIGHT_KEY in styles:
            # copy blob directly from annotations
            styles[LOGO_RIGHT_KEY] = base64.b64encode(
                self.annotations['customstyles'][LOGO_RIGHT_KEY].data)

        return json.dumps(dict(styles))

    def import_styles(self, styles):
        """Imports styles to annotations.
        """
        if LOGO_KEY in styles:
            styles[LOGO_KEY] = StringIO(
                base64.b64decode(styles[LOGO_KEY]))

        if LOGO_RIGHT_KEY in styles:
            styles[LOGO_RIGHT_KEY] = StringIO(
                base64.b64decode(styles[LOGO_RIGHT_KEY]))

        self.save_styles(styles)

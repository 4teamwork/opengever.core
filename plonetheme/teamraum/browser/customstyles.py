from BTrees.OOBTree import OOBTree
from PIL import Image
from plone.app.blob.download import handleIfModifiedSince, handleRequestRange
from plone.i18n.normalizer.interfaces import IUserPreferredFileNameNormalizer
from plonetheme.teamraum.importexport import CustomStylesUtility
from plonetheme.teamraum.importexport import DEFAULT_STYLES
from Products.Archetypes.utils import contentDispositionHeader
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from webdav.common import rfc1123_date
from zope.annotation.interfaces import IAnnotations
from zope.publisher.browser import BrowserView
from plonetheme.teamraum.importexport import LOGO_KEY
from plonetheme.teamraum.importexport import LOGO_RIGHT_KEY


class CustomLogo(BrowserView):

    def __call__(self):
        logo = self.get_logo()
        return logo

    def get_logo(self, disposition='inline', headers=True):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        customstyles_util = CustomStylesUtility(portal)
        customstyles = customstyles_util.annotations.get(
            'customstyles', OOBTree(DEFAULT_STYLES))

        REQUEST = self.request
        RESPONSE = REQUEST.RESPONSE
        blob = LOGO_KEY in customstyles and customstyles[LOGO_KEY] or None
        if not blob:
            return ''
        length = blob.get_size()
        if headers:
            RESPONSE.setHeader('Last-Modified',
                               rfc1123_date(self.context._p_mtime))
            RESPONSE.setHeader('Content-Type', blob.getContentType())
            RESPONSE.setHeader('Accept-Ranges', 'bytes')

            if handleIfModifiedSince(self.context, REQUEST, RESPONSE):
                return ''
            RESPONSE.setHeader('Content-Length', length)
            filename = blob.getFilename()
            if filename is not None:
                filename = IUserPreferredFileNameNormalizer(REQUEST).normalize(
                    unicode(filename, self.context.getCharset()))
                header_value = contentDispositionHeader(
                    disposition=disposition,
                    filename=filename)
                RESPONSE.setHeader("Content-disposition", header_value)

        range = handleRequestRange(self.context, length, REQUEST, RESPONSE)

        return blob.getIterator(**range)


class CustomLogoRight(BrowserView):

    def __call__(self):
        logo = self.get_logo()
        return logo

    def get_logo(self, disposition='inline', headers=True):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        customstyles_util = CustomStylesUtility(portal)
        customstyles = customstyles_util.annotations.get(
            'customstyles', OOBTree(DEFAULT_STYLES))

        REQUEST = self.request
        RESPONSE = REQUEST.RESPONSE
        blob = LOGO_KEY in customstyles and customstyles[LOGO_RIGHT_KEY] or None
        if not blob:
            return ''
        length = blob.get_size()
        if headers:
            RESPONSE.setHeader('Last-Modified',
                               rfc1123_date(self.context._p_mtime))
            RESPONSE.setHeader('Content-Type', blob.getContentType())
            RESPONSE.setHeader('Accept-Ranges', 'bytes')

            if handleIfModifiedSince(self.context, REQUEST, RESPONSE):
                return ''
            RESPONSE.setHeader('Content-Length', length)
            filename = blob.getFilename()
            if filename is not None:
                filename = IUserPreferredFileNameNormalizer(REQUEST).normalize(
                    unicode(filename, self.context.getCharset()))
                header_value = contentDispositionHeader(
                    disposition=disposition,
                    filename=filename)
                RESPONSE.setHeader("Content-disposition", header_value)

        range = handleRequestRange(self.context, length, REQUEST, RESPONSE)

        return blob.getIterator(**range)


class CustomStyles(BrowserView):

    def __call__(self):
        self.css = []
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        annotations = IAnnotations(portal)
        self.customstyles = annotations.get('customstyles',
                                            OOBTree(DEFAULT_STYLES))

        styles = {}
        for k, v in self.customstyles.items():
            styles[k] = v

        self.set_styles()
        return '\n'.join(self.css)

    def set_styles(self):
        # global-navigation
        self.add_boxshadow(
            '#navi-wrapper',
            '0 1px 0 %s inset, 0 0 0 1px %s' % (
                self.get_value_for('css.gnav_shadowinset'),
                self.get_value_for('css.gnav_shadowtop'),
                ),
            '')
        self.add_gradient('#navi-wrapper',
                          self.get_value_for('css.gnav_grad_start'),
                          self.get_value_for('css.gnav_grad_end'))

        self.add_boxshadow(
            '#portal-globalnav li.selected a',
            '0 1px 0 %s inset, 0 -1px 0 %s' % (
                self.get_value_for('css.gnav_active_shadowinset'),
                self.get_value_for('css.gnav_active_shadowtop')),
            ''
            )
        self.add_gradient('#portal-globalnav li.selected a',
                          self.get_value_for('css.gnav_active_start'),
                          self.get_value_for('css.gnav_active_end'))

        self.add_boxshadow(
            '#portal-globalnav a:hover',
            '0 1px 0 %s inset, 0 -1px 0 %s' % (
                self.get_value_for('css.gnav_hover_shadowinset'),
                self.get_value_for('css.gnav_hover_shadowtop')),
            ''
            )
        self.add_gradient('#portal-globalnav a:hover',
                          self.get_value_for('css.gnav_hover_start'),
                          self.get_value_for('css.gnav_hover_end'))

        # mobile navigation
        self.add_style(
            '#portal-globalnav.mobileNavigation, #portal-globalnav.mobileNavigation li a',
            {'background-color': self.get_value_for('css.gnav_hover_start')})
        # mobile navigation (slide)
        self.add_style(
            '#slider-container .slideNavi ul.globalnav li, #slider-container .slideNavi ul.globalnav a, div.slideNavi.loading',
            {'background-color': self.get_value_for('css.gnav_hover_start')})

        # mobile usermenu
        self.css.append("""
            @media screen and (max-width: 769px) {
                #portal-personaltools dd li a,
                #portal-personaltools dd li a:hover,
                #container #portal-searchbox {
                    background-color: %s;
                }
            }""" % self.get_value_for('css.gnav_hover_start'))

        # mobile orgunit-selector
        self.css.append("""
            @media screen and (max-width: 769px) {
                #portal-orgunit-selector dd li a,
                #portal-orgunit-selector dd li a:hover {
                    background-color: %s;
                }
            }""" % self.get_value_for('css.gnav_hover_start'))

        # header
        self.add_style('#header-wrapper, #columns-wrapper',
                       {'background-color': self.get_value_for(
                    'css.header_background')})

        self.add_style('#header',
                       {'height': self.get_value_for('css.header_height')})

        # if logo on the right
        logo_right = self.get_value_for('css.logo_right')
        if logo_right == 'None' or logo_right is None:
            # Hide the logo right wrapper if no logo right is defined
            self.add_style('#portal-logo-right',
                           {'display': 'none'})
        else:
            self.add_style('.headerTop .logo-wrapper',
                           {'width': '22.70916%'})
            self.add_style('.headerTop .controls',
                           {'margin-left': '-74.10359%',
                            'width': '73.70518%'})
            self.add_style('#portal-logo-right',
                           {'float': 'right',
                            'margin-left': '1em'})

        # if headerbox anzeigen
        if self.get_value_for('css.show_headerbox'):
            if self.get_value_for(
                'css.headerbox_background').startswith('rgba'):
                # fix for IE
                self.add_style('div.headerTop',
                               {'background-color': '#fff'})
            self.add_style('div.headerTop',
                           {'margin-top': self.get_value_for(
                        'css.headerbox_spacetop'),
                            'background': self.get_value_for(
                        'css.headerbox_background'),
                            'margin-left': '1%',
                            'margin-right': '1%',
                            'width': '98%',
                            'border-radius': '4px'})
            self.add_style('#portal-personaltools',
                           {'padding-right': '1em'})

            if self.get_value_for('css.logo_spaceleft'):
                self.add_style('div.logo-wrapper',
                               {'padding-left': '1em'})
            else:
                self.add_style('div.logo-wrapper img',
                               {'margin-left': '-4px',
                                'border-radius': '4px 0 0 4px',
                                'moz-border-radius': '4px 0 0 4px',
                                '-webkit-border-radius': '4px 0 0 4px'})

        # if full banner
        if self.get_value_for('css.show_fullbanner'):
            self.add_style('#header', {'position': 'static'})
            self.add_style('#banner-image',
                           {'margin-left': '0',
                            'left': '0',
                            'width': '100%'})
            self.add_style('div.headerTop',
                           {'margin-left': '0',
                            'margin-right': '0',
                            'width': '100%'})

        # content
        self.add_style('#columns-wrapper, .contentWrapper',
                       {'background-color': self.get_value_for(
                    'css.content_background')})

        self.add_style('.fixedWidth',
                       {'width': self.get_value_for('css.content_width')})

        self.add_style('#header-wrapper, #columns-wrapper',
                       {'min-width': self.get_value_for('css.content_width')})

        self.add_style('body',
                       {'font-size': self.get_value_for('css.font_size')})

        self.add_style('a',
                       {'color': self.get_value_for('css.link_color')})

        self.add_style('body',
                       {'color': self.get_value_for('css.text_color')})

        # footer
        self.add_style(
            'body, #footer-wrapper',
            {'background-color': self.get_value_for('css.footer_background')})

        footer_height = 10
        try:
            footer_height = float(self.get_value_for('css.footer_height'))
        except (ValueError, TypeError):
            pass

        self.add_style(
            '#footer',
            {'height': "%sem" % footer_height})

        self.add_style(
            '#footer, .footerPush',
            {'height': "%sem" % footer_height})

        # add 2em because there is a padding in #footer
        self.add_style(
            '.contentWrapper',
            {'margin-bottom': "-%sem" % (footer_height + 2)})

        # fix logo padding
        if LOGO_KEY in self.customstyles:
            self.fix_logo_padding()

        self.add_style(
            '#login-box',
            {'background-color': self.get_value_for(
                    'css.login_background')})

        # additional css
        if self.get_value_for('css.additional_css'):
            self.css.append(self.get_value_for('css.additional_css'))

    def fix_logo_padding(self):
        """Get the images height to fix the padding in the header.
        Checks if the header is big and uses another height to calculate
        padding.
        """
        header_base = 53

        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        view = portal.restrictedTraverse('customlogo', None)
        if view:
            blob = view.get_logo(headers=False)
            if blob:
                img = Image.open(StringIO(blob.read()))
                width, height = img.size
                difference = header_base - height

                if difference <= 0:
                    self.add_style(
                        'div.headerTop div.logo-wrapper',
                        {'margin-top': '0',
                         'margin-bottom': '0'})
                else:
                    self.add_style(
                        'div.headerTop div.logo-wrapper',
                        {'margin-bottom': '%spx' % str(difference / 2),
                         'margin-top': '%spx' % str(difference / 2)})

    def get_value_for(self, key):
        """Checks the values in the annotations for the requested key.
        """
        if key in self.customstyles:
            return str(self.customstyles[key])
        return None

    def add_style(self, selector, rows):
        """Function to add css definitions to a selector.
        """
        if len([value for value in rows.values() if value]) > 0:
            self.css.append(
                "%s {\n  %s\n}" % (
                    selector,
                    '\n  '.join(['%s:%s;' % (k, v) for k, v in rows.items() if v]),
                    )
                )

    def add_boxshadow(self, selector, dimension, color):
        """Adds a box shadow to the selector, using dimension and color.
        """
        self.css.append(
            """
%(selector)s {
  box-shadow: %(dimension)s %(color)s;
  -moz-box-shadow: %(dimension)s %(color)s;
  -webkit-box-shadow: %(dimension)s %(color)s;
}""" % {'selector': selector,
        'dimension': dimension,
        'color': color})

    def add_gradient(self, selector, color_a, color_b):
        """Adds a linear gradient to a specified selector using color_a
        and color_b.
        """
        if color_b and color_b:
            self.css.append(
                """
%(selector)s {
  background-color: %(color_b)s;
  background-image: -moz-linear-gradient(top, %(color_a)s, %(color_b)s);
  background-image: -ms-linear-gradient(top, %(color_a)s, %(color_b)s);
  background-image: -webkit-gradient(linear, 0 0, 0 100%%,\
 from(%(color_a)s), to(%(color_b)s));
  background-image: -webkit-linear-gradient(top, %(color_a)s, %(color_b)s);
  background-image: -o-linear-gradient(top, %(color_a)s, %(color_b)s);
  background-image: linear-gradient(top, %(color_a)s, %(color_b)s);
  filter: progid:DXImageTransform.Microsoft.gradient(\
startColorstr='%(color_a)s', endColorstr='%(color_b)s', GradientType=0);
}
""" % {'selector': selector,
       'color_a': color_a,
       'color_b': color_b}
                )

from Products.CMFCore.utils import getToolByName
from Products.PloneLanguageTool.interfaces import INegotiateLanguage
from zope.globalrequest import getRequest
from zope.interface import implementer


@implementer(INegotiateLanguage)
class NegotiateLanguage(object):
    """Performs language negotiation.

    We replace Plone's default INegotiateLanguage adapter with our own to
    get control over how exactly language negotiation is performed.

    We need to do this in order to also support request language negotiation
    for browsers that only send a simple language preference code (like 'de')
    instead of a combined code like 'de-ch'.
    """

    SIMPLE_TO_COMBINED_MAPPING = {
        'de': 'de-ch',
        'fr': 'fr-ch',
    }

    def getMappedRequestLanguages(self, tool):
        """Get languages from request, but support simple language codes (like
        'de') even though use_combined_language_codes is turned on. This is
        done by explicitly mapping simple codes to combined codes.

        This allows us to consistently end up with combined codes even when
        user agents send simple codes in their Accept-Language header.

        Consistently having combined codes down the line is desirable because
        - production code and tests only need to deal with one form
        - it allows us to take better control over localization aspects (like
          the date format defined in the 'plonelocales' domain)

        This method is heavily based on LanguageTool.getRequestLanguages(),
        but limited to just deal with simple language codes, and only those
        that are actually mapped to a combined language code.

        Therefore the standard getRequestLanguages() still should be triggered
        after invoking this method.
        """
        request = getRequest()

        # Get browser accept languages
        browser_pref_langs = request.get('HTTP_ACCEPT_LANGUAGE', '')
        browser_pref_langs = browser_pref_langs.split(',')

        i = 0
        langs = []
        length = len(browser_pref_langs)

        # Parse quality strings and build a tuple like
        # ((float(quality), lang), (float(quality), lang))
        # which is sorted afterwards
        # If no quality string is given then the list order
        # is used as quality indicator
        for lang in browser_pref_langs:
            lang = lang.strip().lower().replace('_', '-')
            if lang:
                lang_and_qual = lang.split(';', 2)
                quality = []

                if len(lang_and_qual) == 2:
                    try:
                        q = lang_and_qual[1]
                        if q.startswith('q='):
                            q = q.split('=', 2)[1]
                            quality = float(q)
                    except:  # noqa
                        pass

                if quality == []:
                    quality = float(length - i)

                language = lang_and_qual[0]

                if '-' in language:
                    # Already a combined language code
                    continue

                if language not in self.SIMPLE_TO_COMBINED_MAPPING:
                    # Not a mapped language
                    continue

                # Map simple code to combined language code, and add it as
                # negotiated language (if it's actually supported).
                language = self.SIMPLE_TO_COMBINED_MAPPING[language]
                if language in tool.getSupportedLanguages():
                    langs.append((quality, language))

                i = i + 1

        # Sort and reverse it
        langs.sort()
        langs.reverse()

        # Filter quality string
        langs = map(lambda x: x[1], langs)

        return langs

    def __init__(self, site, request):
        """Perform language negotiaton.

        Directly based on LanguageTool.NegotiateLanguage.__init__.

        The only difference is the call to our own getMappedRequestLanguages()
        before the standard request language negotiation.
        """
        tool = getToolByName(site, 'portal_languages')
        langs = []
        useContent = tool.use_content_negotiation
        useCcTLD = tool.use_cctld_negotiation
        useSubdomain = tool.use_subdomain_negotiation
        usePath = tool.use_path_negotiation
        useCookie = tool.use_cookie_negotiation
        setCookieEverywhere = tool.set_cookie_everywhere
        authOnly = tool.authenticated_users_only
        useRequest = tool.use_request_negotiation
        useDefault = 1  # This should never be disabled
        langsCookie = None

        if usePath:
            # This one is set if there is an allowed language in the current path
            langs.append(tool.getPathLanguage())

        if useContent:
            langs.append(tool.getContentLanguage())

        if useCookie and not (authOnly and tool.isAnonymousUser()):
            # If we are using the cookie stuff we provide the setter here
            set_language = tool.REQUEST.get('set_language', None)
            if set_language:
                langsCookie = tool.setLanguageCookie(set_language)
            else:
                # Get from cookie
                langsCookie = tool.getLanguageCookie()
            langs.append(langsCookie)

        if useSubdomain:
            langs.extend(tool.getSubdomainLanguages())

        if useCcTLD:
            langs.extend(tool.getCcTLDLanguages())

        # Get langs from request
        if useRequest:
            # Before doing the standard request language negotiation, we
            # do our own to map simple lang codes like 'de' to combined codes
            # like 'de-ch'. This is the only difference to the default
            # implementation from LanguageTool.NegotiateLanguage
            langs.extend(self.getMappedRequestLanguages(tool))

        if useRequest:
            langs.extend(tool.getRequestLanguages())

        # Get default
        if useDefault:
            langs.append(tool.getDefaultLanguage())

        # Filter None languages
        langs = [lang for lang in langs if lang is not None]

        # Set cookie language to language
        if setCookieEverywhere and useCookie and langs[0] != langsCookie:
            tool.setLanguageCookie(langs[0], noredir=True)

        self.default_language = langs[-1]
        self.language = langs[0]
        self.language_list = langs[1:-1]

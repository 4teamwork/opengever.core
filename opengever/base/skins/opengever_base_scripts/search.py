# This view is needed because the search skin template
# is still in the `plone_depracted` folder and therfore active.
# This file should be removed when the search template is dropped
# out of the `plone_deprecated` skins folder

return context.REQUEST.RESPONSE.redirect('@@search')

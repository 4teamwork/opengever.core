## Script (Python) "before_open_resolved"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=state_change
##title=
##

return context.restrictedTraverse('copy-related-documents-to-inbox')(state_change)

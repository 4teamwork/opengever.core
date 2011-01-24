## Controller Python Script "folder_paste"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Paste objects into a folder
##

if context.REQUEST['__cp']:
    objlist = context.REQUEST['__cp'].split(':')
    for obj in objlist:
        context.manage_pasteObjects(obj)
return context.REQUEST.RESPONSE.redirect(context.absolute_url())
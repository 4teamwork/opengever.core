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


redirect_view = ''
if context.REQUEST.get('__cp'):
    objid = ''
    objlist = context.REQUEST['__cp'].split(':')
    for obj in objlist:
        objid = context.manage_pasteObjects(obj)
    myobj = context.get(objid[0]['new_id'])
    if myobj.portal_type == 'opengever.document.document':
        redirect_view = '#documents'
    elif myobj.portal_type == 'opengever.task.task':
        redirect_view = '#task'
    elif myobj.portal_type == 'opengever.dossier.businesscasedossier':
        redirect_view = '#dossiers'
return context.REQUEST.RESPONSE.redirect(context.absolute_url()+ redirect_view)
from opengever.ogds.base.utils import get_client_id


def documents_list_helper(context, items):
    urlstring = ''
    lastindex = len(items)-1
    for i, item in enumerate(items):
        if lastindex == i:
            urlstring = urlstring + '<span><a href="./@@resolve_oguid?oguid='+\
                        get_client_id()+':'+str(item['intid'])+'">'+\
                        item['title']+'</a></span>'
        else:
            urlstring = urlstring + '<span><a href="./@@resolve_oguid?oguid='+\
                        get_client_id()+':'+str(item['intid'])+'">'+\
                        item['title']+', </a></span>'
    return urlstring

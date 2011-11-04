
def documents_list_helper(items):
    urlstring = ''
    for item in items:
        urlstring = urlstring + '<span><a href="'+item['url']+'">'+item['title']+'</a></span>'
    return urlstring
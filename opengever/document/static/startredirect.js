startRedirect = function(){
    if (location.search.search('redirectTo=') != -1){
        temp = location.search;
        temp = temp.substr(temp.search('redirectTo') + 11, temp.length);
        if (temp.search('&') != -1){
            temp = temp.substr(0, temp.search('&'));
        }
        location.href = portal_url+unescape(temp);
    }
    $('.tabbedview_view').unbind('reload', startRedirect);
}

$(function(){
    $('.tabbedview_view').bind('reload', startRedirect);
});
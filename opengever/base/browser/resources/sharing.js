jq(function() {
    jq('.link-overlay').prepOverlay({
        subtype:'ajax',
        urlmatch:'$',
        urlreplace:''
        });
    console.info('done');

    /*
    jq('div.sharing_group').each(function(){
        obj = jq(this);
        html = obj.html();
        group_id = obj.attr('id');
        new_html = '<a href="#" rel="'+group_id+'" class="show_members">';
        new_html += html;
        new_html += '</a>';
        obj.html(new_html);
    });
    */

    /*
    jq('.show_members').live('click', function(e){
        obj = jq(this);
        jq.ajax({type : 'POST',
             url : './list_groupmembers',
             success : function(data, textStatus, XMLHttpRequest) {
                 if (data.length > 0) {
                     
                     jq('#members_'+obj.attr('rel')).html(data);
                 }
             }
        });
        e.preventDefault();
    });
    */
});
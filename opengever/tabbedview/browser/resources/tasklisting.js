jq(function(){

    review_state_filter = function(set_filter){
        
        tabbedview.prop('review_state', set_filter);
        tabbedview.reload_view();
    };
    
    activate_filters = function(set_filter){
        console.info('active filters');
        if(tabbedview.prop('review_state')){
            jq('#filter_open').css('color', 'red');
        }
        else{
            jq('#filter_all').css('color', 'red');
        }
    };

    jq('.tabbedview_view').live('reload', function(){activate_filters(false);});

});

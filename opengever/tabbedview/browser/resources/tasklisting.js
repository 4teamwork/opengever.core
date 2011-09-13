jq(function(){

    review_state_filter = function(set_filter){
        
        tabbedview.prop('review_state', set_filter);
        tabbedview.reload_view();
    };
    
    activate_filters = function(set_filter){
        console.info('activate_filters');
        if(tabbedview.prop('review_state')){
            console.info('RED OPEN');
            jq('#filter_open').css('color', 'red');
        }
        else{
            jq('#filter_all').css('color', 'red');
            console.info('RED ALL');
        }
    };
    
    // jq('.tabbedview_view').bind('reload', activate_filters(false));

});

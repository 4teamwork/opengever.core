jq(function(){

    review_state_filter = function(set_filter){

        tabbedview.prop('review_state', set_filter);
        tabbedview.reload_view();
    };

    activate_filters = function(set_filter){
        if(tabbedview.prop('review_state')){
            jq('#filter_open').addClass('active');
            jq('#all_open').removeClass('active');
        }
        else{
            jq('#filter_open').removeClass('active');
            jq('#all_open').addClass('active');
        }
    };

    jq('#filter_all').live('click', function(){review_state_filter(false);});
    jq('#filter_open').live('click', function(){review_state_filter(true);});

    jq('.tabbedview_view').live('reload', function(){activate_filters(false);});
});

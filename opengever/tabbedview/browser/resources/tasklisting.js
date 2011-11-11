jq(function(){

    review_state_filter = function(set_filter){
        tabbedview.prop('review_state', set_filter);
        tabbedview.reload_view();
    };

    jq('#filter_all').live('click', function(){review_state_filter(false);});
    jq('#filter_open').live('click', function(){review_state_filter(true);});
});

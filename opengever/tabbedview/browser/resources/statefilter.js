$(function(){

    review_state_filter = function(set_filter){
        tabbedview.prop('review_state', set_filter);
        tabbedview.reload_view();
    };

    $('#filter_all').live('click', function(){review_state_filter(false);});
    $('#filter_open').live('click', function(){review_state_filter(true);});
});

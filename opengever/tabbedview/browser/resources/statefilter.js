$(function(){

    review_state_filter = function(set_filter, link){
        state_filter_name = link.parents('.state_filters').attr('id');
        tabbedview.prop(state_filter_name, set_filter);
        tabbedview.reload_view();
    };

    $('#filter_all').live('click', function(){
      review_state_filter(false, $(this));
    });

    $('#filter_open').live('click', function(){
      review_state_filter(true, $(this));
    });
});

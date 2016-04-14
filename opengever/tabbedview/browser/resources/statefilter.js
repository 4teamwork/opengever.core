$(function(){
  $('.state_filters a').live('click', function(){
    state_filter_name = $(this).parents('.state_filters').attr('id');
    tabbedview.prop(state_filter_name, $(this).attr('id'));
    tabbedview.reload_view();
  });

});

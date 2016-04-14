$(function(){
  $('.state_filters a').live('click', function(){
    filterlist_name = $(this).parents('.state_filters').attr('id');
    tabbedview.prop(filterlist_name, $(this).attr('id'));
    tabbedview.reload_view();
  });

});

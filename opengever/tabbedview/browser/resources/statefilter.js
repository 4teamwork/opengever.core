var initSubjectFilterWidget = function() {
  var widget = $('.keyword-widget');
  if (widget.length <= 0) { return; }

  window.ftwKeywordWidget.initWidget(widget);
    widget.on('select2:opening', function (e) {
      if (widget.loading) {
        e.preventDefault();
      }
    });
    widget.on('change.select2', function () {
      var data = widget.val() || [];
      widget.loading = true;
      tabbedview.prop('subjects', data.join('++'));
      tabbedview.reload_view();
    });
  };

$(document).on('reload gridRendered', '.tabbedview_view', function() {
    initSubjectFilterWidget();
});

$(function(){


  $('.state_filters a').live('click', function(){
    filterlist_name = $(this).parents('.state_filters').attr('id');
    tabbedview.prop(filterlist_name, $(this).attr('id'));
    tabbedview.reload_view();
  });

});

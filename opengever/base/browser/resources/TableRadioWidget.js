$(function() {
  $('.tableradio-widget-wrapper[data-vocabulary-depends-on]').each(function() {
    /** When a table radio widget has a list of fieldnames configured
        in  "vocabulary-depends-on", the widget should be re-rendered
        whenever one of those fields change, so that the vocabulary
        can reduce its selectable terms. **/

    var widget = $(this);
    var fieldname = widget.parent('.field').data('fieldname');
    var form = widget.parents('form:first');
    var dependency_fields_selector = widget.data('vocabulary-depends-on').map(function(fieldname) {
      return '[name="' + fieldname + '"], [name="' + fieldname + ':list"]'; }).join(',');
    var dependency_fields = $(dependency_fields_selector);

    var update_widget = function() {
      var selection = widget.find('input[type=radio]:checked').val();
      var widget_render_url = [location.protocol, '//', location.host,
                               location.pathname,
                               '/++widget++' + fieldname,
                               '/ajax_render'].join('');
      $.get(widget_render_url,
            form.serialize(),
            function(result) {
              widget.html($(result).find('.tableradio-widget-wrapper'));
              widget.find('input[value="' + selection + '"]').prop('checked', true);
            });
    };

    $(dependency_fields).change(update_widget);
    update_widget();
  });
});

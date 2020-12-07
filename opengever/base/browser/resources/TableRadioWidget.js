$(function() {
  function tableradio_searchfilter() {
    var filter = $(this);
    var text = filter.val().toUpperCase();
    var widget = filter.closest('.tableradioSearchboxContainer').next('.tableradio-widget-wrapper');
    var tr = widget.find('tbody tr');
    var td;

    tr.each(function(_, tr) {
      // Second cell is the title
      td = tr.cells[1];
      tr = $(tr);

      if (unorm.nfc(td.textContent.trim().toUpperCase()).indexOf(unorm.nfc(text)) > -1) {
        tr.show();
      } else {
        tr.hide();
      }
    });
  }

  $('.tableradioSearchbox').on('input', tableradio_searchfilter);

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
      var widget_render_url = [form.attr('action'),
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

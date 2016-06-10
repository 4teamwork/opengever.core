$(function() {
  $('.link-overlay').live('click', function(event) {

    event.preventDefault();

    var events = $(this).data('events');

    if (!events || !events.click) {
      $(this).prepOverlay({
        subtype: 'ajax',
        urlmatch: '$',
        urlreplace: '',
        config: { expose: { color: "#000" } }
      });

      $(this).trigger('click');
    }

  });
});

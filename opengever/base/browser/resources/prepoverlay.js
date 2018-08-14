$(function() {
  $('.link-overlay').live('click', function(event) {

    event.preventDefault();

    var config = {
      subtype: 'ajax',
      urlmatch: '$',
      urlreplace: '',
      config: {
        mask: {
          color: "#fff"
        }
      }
    };

    if($(event.currentTarget).hasClass("modal")) {
      config.config.mask.color = "#000";
    }

    var events = $(this).data('events');

    if ($(this).parents('.overlay-ajax').length) {
      $(this).parents('.overlay-ajax').overlay().close();
    };

    if (!events || !events.click) {
      $(this).prepOverlay(config);

      $(this).trigger('click');
    }

  });
});

(function(global, $) {

  "use strict";

  var Rangetimepicker = function(options) {

    options = $.extend({
      precision: 5, // in minutes
      target: {
        start: ".datetimepicker-start",
        end: ".datetimepicker-end"
      }
    }, options);

    var self = this;

    this.start = options.target.start;
    this.end = options.target.end;

    if (!this.start.length || !this.end.length) {
      // Rangetimepicker is only used in some views, namely when there's a start _and_ an end field.
      return;
    }

    this.startwidget = this.start.data('xdsoft_datetimepicker').data('xdsoft_datetime');
    this.endwidget = this.end.data('xdsoft_datetimepicker').data('xdsoft_datetime');

    var roundMinutes = function(date) {
      return new Date(date.setMinutes(Math.ceil(date.getMinutes() / options.precision) * options.precision));
    };

    if (!this.start.val()) {
      var roundedStartDateTime = roundMinutes(this.startwidget.getCurrentTime());
      this.start.val(this.startwidget.str(roundedStartDateTime));
    }

    // make sure no date is selected before the start of the range by looking
    // up the earliest valid time in the startwidget
    self.end.datetimepicker({
      onShow: function (current_time, input) {
                this.setOptions({
                  minDate: self.startwidget.getCurrentTime(),
                  minTime: self.startwidget.getCurrentTime()
                });
              }
    });

    // avoid ftw.datetimepicker destroying our end datetime picker 
    $(document).off('change', '.datetimepicker-widget');
  };

  $(function() {

    var start = $("#form-widgets-start");
    var end = $("#form-widgets-end");

    var options = {
      target: {
        start: start,
        end: end
      }
    };

    var range = new Rangetimepicker(options);

  });

}(window, window.jQuery));

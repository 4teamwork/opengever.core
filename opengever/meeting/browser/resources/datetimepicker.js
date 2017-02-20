(function(global, $) {

  "use strict";

  var Rangetimepicker = function(options) {

    options = $.extend({
      minRange: 1,  // in hours
      precision: 5, // in minutes
      target: {
        start: ".datetimepicker-start",
        end: ".datetimepicker-end"
      }
    }, options);

    var self = this;

    this.start = options.target.start;
    this.end = options.target.end;

    if (!this.start.length || !this.start.length) {
      return;
    }

    this.startwidget = this.start.data('xdsoft_datetimepicker').data('xdsoft_datetime');
    this.endwidget = this.end.data('xdsoft_datetimepicker').data('xdsoft_datetime');

    var roundMinutes = function(date) {
      return new Date(date.setMinutes(Math.ceil(date.getMinutes() / options.precision) * options.precision));
    };

    var updateSelectableDates = $.proxy(function(){
      self.end.datetimepicker({minDate: self.startwidget.getCurrentTime(),
                               minTime: self.startwidget.getCurrentTime()})
    });

    var adjustEndtime = $.proxy(function(start) {
      var end = new Date(start.setHours(start.getHours() + options.minRange));
      this.endwidget.setCurrentTime(end);
      this.end.val(this.endwidget.str(end));
    }, this);

    var updateDate = $.proxy(function(date) {
      if(options.minRange && (this.endwidget.getCurrentTime() - date) < (options.minRange * 60 * 60 * 1000)) {
        adjustEndtime(date);
      } else if (!this.end.val()) {
        adjustEndtime(date);
      }
    }, this);

    if (!this.start.val()) {
      var roundedStartDateTime = roundMinutes(this.startwidget.getCurrentTime());
      this.start.val(this.startwidget.str(roundedStartDateTime));
    }
    updateSelectableDates();

    this.start.on('change', function(event) {
        // Bug in dateptimeicker - the internal state is not updated after clearing the field.
        var date = self.startwidget.strToDateTime($(this).val());
        self.startwidget.setCurrentTime(date);
        updateDate(date);
        updateSelectableDates();
      });
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

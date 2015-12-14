(function(global, $) {

  "use strict";

  $.fn.datetimepicker.dates.de = $.fn.datetimepicker.dates["de-ch"] = {
    days: ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"],
    daysShort: ["Son", "Mon", "Die", "Mit", "Don", "Fre", "Sam", "Son"],
    daysMin: ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"],
    months: ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
    monthsShort: ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"],
    today: "Heute",
    suffix: [],
    meridiem: [],
    weekStart: 1,
    format: "dd.mm.yyyy hh:ii"
  };

  $.fn.datetimepicker.dates.fr = $.fn.datetimepicker.dates["fr-ch"] = {
    days: ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"],
    daysShort: ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
    daysMin: ["D", "L", "Ma", "Me", "J", "V", "S", "D"],
    months: ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"],
    monthsShort: ["Jan", "Fev", "Mar", "Avr", "Mai", "Jui", "Jul", "Aou", "Sep", "Oct", "Nov", "Dec"],
    today: "Aujourd'hui",
    suffix: [],
    meridiem: [],
    weekStart: 1,
    format: "dd.mm.yyyy hh:ii"
  };

  $.fn.datetimepicker.dates.en = {
    days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    daysShort: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    daysMin: ["Su", "Mop", "Tu", "We", "Th", "Fr", "Sa", "Su"],
    months: ["January", "Febrauary", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    monthsShort: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    today: "Today",
    suffix: [],
    meridiem: [],
    weekStart: 1,
    format: "dd/mm/yyyy hh:ii"
  };

  // Confirmend bug in https://github.com/smalot/bootstrap-datetimepicker/issues/122
  var applyTimezone = function(date) { return new Date(date.setTime(date.getTime() + (date.getTimezoneOffset() * 60 * 1000))); };

  var Datetimepicker = function(options) {

    var lang = $("#ploneLanguage").data("lang");

    options = $.extend({
      target: ".datetimepicker",
      autoclose: true,
      todayHighlight: true,
      todayBtn: true,
      startView: 1,
      minuteStep: 5,
      viewSelect: "year",
      language: lang
    }, options);

    this.element = $(options.target);

    var roundMinutes = function(date, precision) { return new Date(date.setMinutes(Math.ceil(date.getMinutes() / precision) * precision)); };

    var getUTCDate = function(date) { return new Date(date + "UTC"); };

    var convertToLocalTime = function(date) { return applyTimezone(date); };

    this.date = roundMinutes(getUTCDate(new Date()), options.minuteStep);

    this.element.datetimepicker(options);

    this.on = function(event, callback) { this.element.on(event, callback); };

    this.setStartDate = function(date) { this.element.datetimepicker("setStartDate", convertToLocalTime(new Date(date))); };

    this.setEndDate = function(date) { this.element.datetimepicker("setEndDate", convertToLocalTime(new Date(date))); };

    this.setDate = function(date) {
      this.date = new Date(date);
      var localTime = convertToLocalTime(new Date(date));
      this.element.datetimepicker("setDate", localTime);
    };

    this.setDate(this.date);

  };

  var Rangetimepicker = function(options) {

    options = $.extend({
      minRange: 1,
      target: {
        start: ".datetimepicker-start",
        end: ".datetimepicker-end"
      }
    }, options);

    var self = this;

    this.start = new Datetimepicker({ target: options.target.start });
    this.end = new Datetimepicker({ target: options.target.end });

    var adjustEndtime = $.proxy(function(start) {
      var end = new Date(new Date(start).setHours(start.getHours() + options.minRange));
      this.end.setDate(end);
    }, this);

    var updateDate = $.proxy(function(date) {
      if(options.minRange && (this.end.date - date) < (options.minRange * 60 * 60 * 1000)) {
        adjustEndtime(date);
      }
      this.end.setStartDate(date);
      this.start.setDate(date);
    }, this);

    updateDate(this.start.date);

    this.start.on("changeDate", function(event) { updateDate(event.date); });
    this.end.on("changeDate", function(event) { self.end.setDate(event.date); });

  };

  $(function() {

    var start = $("<input class='spv-datetime-widget' type='text' />");
    var end = $("<input class='spv-datetime-widget' type='text' />");

    start.insertAfter("#formfield-form-widgets-start > label");
    end.insertAfter("#formfield-form-widgets-end > label");

    var range = new Rangetimepicker({
      target: {
        start: start,
        end: end
      }
    });

    var applyPloneWidget = function() {
      var startDate = applyTimezone(new Date(range.start.date));
      $("#form-widgets-start-day").attr("value", startDate.getDate());
      $("#form-widgets-start-month").attr("value", startDate.getMonth() + 1);
      $("#form-widgets-start-year").attr("value", startDate.getFullYear());
      $("#form-widgets-start-hour").attr("value", startDate.getHours());
      $("#form-widgets-start-min").attr("value", startDate.getMinutes());

      var endDate = applyTimezone(new Date(range.end.date));
      $("#form-widgets-end-day").attr("value", endDate.getDate());
      $("#form-widgets-end-month").attr("value", endDate.getMonth() + 1);
      $("#form-widgets-end-year").attr("value", endDate.getFullYear());
      $("#form-widgets-end-hour").attr("value", endDate.getHours());
      $("#form-widgets-end-min").attr("value", endDate.getMinutes());
    };

    range.start.on("changeDate", applyPloneWidget);
    range.end.on("changeDate", applyPloneWidget);

    applyPloneWidget();


  });


}(window, jQuery));

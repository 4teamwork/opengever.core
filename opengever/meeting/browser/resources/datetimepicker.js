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

  var Datetimepicker = function(initialDate, options) {

    var lang = $("#ploneLanguage").data("lang");

    var clearBtn = $("<a href='#' class='spv-datetime-widget-clear'>");

    options = $.extend({
      target: ".datetimepicker",
      autoclose: true,
      todayHighlight: true,
      todayBtn: true,
      startView: 1,
      minuteStep: 5,
      viewSelect: "year",
      language: lang,
      clearBtn: false
    }, options);

    this.blank = true;

    this.element = $(options.target);

    clearBtn.on("click", function(event) {
      event.preventDefault();
      this.clear();
    }.bind(this));

    if(options.clearBtn) {
      clearBtn.insertAfter(this.element);
    }

    var roundMinutes = function(date, precision) {
      return new Date(date.setMinutes(Math.ceil(date.getMinutes() / precision) * precision));
    };

    this.element.datetimepicker(options);

    this.on = function(event, callback) { this.element.on(event, callback); };

    this.setStartDate = function(date) { this.element.datetimepicker("setStartDate", date); };

    this.setEndDate = function(date) { this.element.datetimepicker("setEndDate", date); };

    this.setDate = function(date) {
      this.blank = false;
      this.element.datetimepicker("setDate", date);
      this.element.trigger("date-changed", [date]);
    };

    this.getDate = function() { return this.element.datetimepicker("getDate"); };

    this.clear = function() {
      this.blank = true;
      this.element.val("");
      this.element.trigger("date-cleared");
      this.element.trigger("input");
    };

    if(initialDate) {
      this.setDate(roundMinutes(initialDate, options.minuteStep));
    }

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

    this.start = new Datetimepicker(options.start || new Date(), { target: options.target.start });
    this.end = new Datetimepicker(options.end, { target: options.target.end, clearBtn: true });

    var adjustEndtime = $.proxy(function(start) {
      var end = new Date(new Date(start).setHours(start.getHours() + options.minRange));
      this.end.setDate(end);
    }, this);

    var updateDate = $.proxy(function(date) {
      if(options.minRange && (this.end.getDate() - date) < (options.minRange * 60 * 60 * 1000)) {
        adjustEndtime(date);
      }
      this.end.setStartDate(date);
      this.start.setDate(date);
    }, this);

    if(!this.end.blank) {
      updateDate(this.start.getDate());
    } else {
      this.end.setStartDate(this.start.getDate());
    }

    this.start.on("changeDate", function(event) { updateDate(event.date); });
    this.end.on("changeDate", function(event) { self.end.setDate(event.date); });

  };

  $(function() {

    var start = $("<input class='spv-datetime-widget' readonly type='text' />");
    var end = $("<input class='spv-datetime-widget' readonly type='text' />");

    start.insertAfter("#formfield-form-widgets-start > label");
    end.insertAfter("#formfield-form-widgets-end > label");

    var parsePloneWidgetStart = function() {
      var startDate = new Date();

      startDate.setDate($("#form-widgets-start-day").attr("value"));
      startDate.setMonth($("#form-widgets-start-month").attr("value") - 1);
      startDate.setFullYear($("#form-widgets-start-year").attr("value"));
      startDate.setHours($("#form-widgets-start-hour").attr("value"));
      startDate.setMinutes($("#form-widgets-start-min").attr("value"));

      return startDate;
    };

    var parsePloneWidgetEnd = function() {
      var endDate = new Date();
      endDate.setDate($("#form-widgets-end-day").attr("value"));
      endDate.setMonth($("#form-widgets-end-month").attr("value") - 1);
      endDate.setFullYear($("#form-widgets-end-year").attr("value"));
      endDate.setHours($("#form-widgets-end-hour").attr("value"));
      endDate.setMinutes($("#form-widgets-end-min").attr("value"));
      return endDate;
    };

    var applyStartWidget = function(date) {
      $("#form-widgets-start-day").attr("value", date.getDate());
      $("#form-widgets-start-month").attr("value", date.getMonth() + 1);
      $("#form-widgets-start-year").attr("value", date.getFullYear());
      $("#form-widgets-start-hour").attr("value", date.getHours());
      $("#form-widgets-start-min").attr("value", date.getMinutes());
    };

    var applyEndWidget = function(date) {
      $("#form-widgets-end-day").attr("value", date.getDate());
      $("#form-widgets-end-month").attr("value", date.getMonth() + 1);
      $("#form-widgets-end-year").attr("value", date.getFullYear());
      $("#form-widgets-end-hour").attr("value", date.getHours());
      $("#form-widgets-end-min").attr("value", date.getMinutes());
    };

    var clearEndWidget = function() {
      $("#form-widgets-end-day").attr("value", null);
      $("#form-widgets-end-month").attr("value", null);
      $("#form-widgets-end-year").attr("value", null);
      $("#form-widgets-end-hour").attr("value", null);
      $("#form-widgets-end-min").attr("value", null);
    };

    var options = {
      target: {
        start: start,
        end: end
      }
    };

    if($("#form-widgets-start-day").attr("value") !== "") {
      options.start = parsePloneWidgetStart();
    }

    if($("#form-widgets-end-day").attr("value") !== "") {
      options.end = parsePloneWidgetEnd();
    }

    var range = new Rangetimepicker(options);

    range.start.on("date-changed", function(event, date) { applyStartWidget(date); });
    range.end.on("date-changed", function(event, date) { applyEndWidget(date); });
    range.end.on("date-cleared", function() { clearEndWidget(); });

    applyStartWidget(range.start.getDate());

  });


}(window, window.jQuery));

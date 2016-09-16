(function(global, $) {

  function Synchronizer(options) {

    this.options = $.extend({
      delay: 1000,
      target: document,
      context: document,
      triggers: []
    }, options || {});

    var self = this;

    var syncCallback = $.noop;

    var trackType = function(event) {
      clearTimeout(this.timeout);
      this.timeout = setTimeout(function() { syncCallback(event.target); }, self.options.delay);
    };

    this.observe = function() { $(this.options.context).on(this.options.triggers.join(" "), this.options.target, trackType); };

    this.onSync = function(callback) { syncCallback = callback; };

  }

  global.Synchronizer = Synchronizer;

})(window, window.jQuery);

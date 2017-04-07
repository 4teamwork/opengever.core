(function($) {

  var HttpCodes = {
    FORBIDDEN: 403,
    OK: 200
  }

  var filter = {
    filters: {},
    add: function(code, filter) {
      this.filters[code] = function(_, _, jqXHR) { filter(jqXHR); }
    },
    apply: function(_, _, jqXHR) {
      console.log(this.filters);
      jqXHR.statusCode(this.filters);
    }
  };

  filter.add(HttpCodes.FORBIDDEN,function(jqXHR) {
    jqXHR.abort();
  });

  filter.add(HttpCodes.OK, function(jqXHR) {
    console.log("okay");
  });

  $.ajaxPrefilter(filter.apply.bind(filter));

})(window.jQuery);

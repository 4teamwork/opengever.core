(function(global, $, Controller, Handlebars) {
  "use strict";

  // XXX - We only have to filter out in-template as the API design is silly
  Handlebars.registerHelper('ifNot', function(a, b, options) {
    if(a !== b) {
      return options.fn(this);
    }
    return options.inverse(this);
  });

  function ConfigTableController(options) {
    global.Controller.call(this, $('#config_table_template').html(), $('#config_table'), options);
    // We're guaranteed the HTML and JSON endpoints are on /@config
    this.fetch = function(){return $.ajax({url: '', type: 'GET', headers: {'Accept': 'application/json'}});};
    this.render = function(data) {return this.template({config: data});};
    this.init();
  }

  $(function() {
    if($("#config_table_template").length) {
      var configTableController = new ConfigTableController();
    }

  });

}(window, window.jQuery, window.Controller, window.Handlebars));

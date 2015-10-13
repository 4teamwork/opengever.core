(function($){

  "use strict";

  function Scrollspy(_options) {

    var options = $.extend({
      selector: "#scrollspy",
      selectParent: false
    }, _options || {});

    var scrollCallback = function() {};
    var selectCallback = function() {};

    function init() {
      $(options.selector + " a").click(function(event) {
        event.preventDefault();
        var target = $(event.target);
        if(target.hasClass("paragraph")) {
          scrollTo(target.parent().next().find("> a"));
        } else {
          scrollTo(event.target);
        }
      });
    }

    function scrollTo(target) {
      var target = $(target)
      var toElement = $(target.attr("href"));
      var offset = 0;
      if(!target.hasClass("expandable")) {
        offset = options.offset;
      }
      $('html, body').scrollTop(toElement.offset().top - (offset) + 1);
      scrollCallback(target, toElement);
    }

    function select(target) {
      target = $(target);
      $(options.selector + " .selected").not(target).removeClass("selected");
      target.addClass("selected");
      if(options.selectParent) {
        var parent = target.closest("ul").prev("a.expandable");
        $(options.selector + " .selected").not(target).not(parent).removeClass("selected");
        parent.addClass("selected")
      }
      selectCallback(target);
    }

    function expand(target) {
      $(options.selector + " .expandable").not(target).removeClass("expanded");
      $(target).addClass("expanded");
    }

    function reset() {
      $(options.selector + " .expandable").removeClass("expanded");
      $(options.selector + " .selected").removeClass("selected");
    }

    init();

    var app = {

      scrollTo: function(target) {
        scrollTo(target);
      },

      select: function(target) {
        select(target);
      },

      onScroll: function(callback) {
        scrollCallback = callback;
      },

      onSelect: function(callback) {
        selectCallback = callback;
      },

      expand: function(target) {
        expand(target);
      },

      offset: function(offset) {
        options.offset = offset;
      },

      reset: function() {
        reset();
      }

    };

    return app;

  }

  window.Scrollspy = Scrollspy;

}(jQuery));
(function($){

  "use strict";

  function StickyHeading(_options) {

    var onStickyCallback = function() {};
    var onNoStickyCallback = function() {};
    var onCollisionCallback = function() {};

    var options = $.extend({ refresh: true, fix: true }, _options || {});

    var currentSticky;

    var currentHeadings;

    var layouter = {

      initHeadings: function(selector) {
        return $(selector).map(function(i, e) {
          var el = $(e);
          var clone = el.clone();
          clone.attr("id", el.attr("id") + "_clone");
          clone.insertAfter(el);
          clone.addClass("clone");
          var heading = { node: el, offset: el.offset().top, height: el.outerHeight(), clone: clone }
          el.addClass("original");
          return heading;
        });
      },

      updateOffsets: function(headings) {
        return $.each(headings, function(i, e){
          e.offset = e.node.offset().top;
        });
      },

      findPastHeadings: function(headings, scrollPositionTop) {
        return $.grep(headings, function(heading) {
          return scrollPositionTop >= heading.offset;
        });
      },

      observe: function(selector) {
        var self = this;
        var currentHeadings = this.initHeadings(selector);
        $(window).scroll(function() { self.onScroll(currentHeadings) });
      },

      onScroll: function(headings) {
        if(options.refresh) {
          headings = this.updateOffsets(headings);
        }
        if(options.fix) {
          this.reset(headings);
        }
        var scrollPositionTop = $(window).scrollTop();
        var pastHeadings = this.findPastHeadings(headings, scrollPositionTop);
        var offsetHeight = 0;

        if(options.dependsOn && options.dependsOn.getSticky()) {
          offsetHeight = options.dependsOn.getSticky().clone.outerHeight();
        }

        if (pastHeadings.length > 0) {
          var sticky = pastHeadings[pastHeadings.length - 1];
          var nextHeading = headings[headings.index(sticky) + 1];
          if (nextHeading && scrollPositionTop >= nextHeading.offset - (sticky.height + offsetHeight)) {
            this.collision(sticky, nextHeading, scrollPositionTop);
          } else {
            this.sticky(sticky, scrollPositionTop);
          }
        } else {
          this.noSticky(scrollPositionTop);
        }
      },

      reset: function(headings){
        $.each(headings, function(i, heading) { heading.clone.removeClass('sticky').css('top', 0); });
      },

      noSticky: function(scrollPositionTop){
        onNoStickyCallback(scrollPositionTop);
      },

      sticky: function(heading, scrollPositionTop){
        if(options.fix) {
          heading.clone.addClass('sticky');
          heading.clone.css('top', scrollPositionTop - heading.offset);
        }
        currentSticky = heading;
        onStickyCallback(heading, scrollPositionTop);
      },

      collision: function(fadeOutHeading, fadeInHeading, scrollPositionTop) {
        if(options.fix) {
          fadeOutHeading.clone.addClass('sticky').css('top', fadeInHeading.offset - fadeOutHeading.offset - fadeOutHeading.height);
          fadeInHeading.clone.addClass('sticky');
        }
        onCollisionCallback(fadeOutHeading, fadeInHeading, scrollPositionTop);
      }
    };

    layouter.observe(options.selector);

    var app = {};

    app.onSticky = function(callback) {
        onStickyCallback = callback;
    };

    app.onNoSticky = function(callback) {
      onNoStickyCallback = callback;
    };

    app.onCollision = function(callback) {
      onCollisionCallback = callback;
    };

    app.getSticky = function() {
      return currentSticky;
    };

    return app;

  }

  window.StickyHeading = StickyHeading;

}(jQuery));

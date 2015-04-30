stickyHeading = function($){

  var onStickyCallback = function() {};
  var onNoStickyCallback = function() {};
  var onCollisionCallback = function() {};

  var layouter = {
    reset: function(headings){
      $.each(headings, function(i, heading) { heading.node.removeClass('sticky').css('top', 0); });
    },

    noSticky: function(scrollPositionTop){
      onNoStickyCallback(scrollPositionTop);
    },

    sticky: function(heading, pastHeading, scrollPositionTop){
      heading.node.addClass('sticky');
      heading.node.css('top', scrollPositionTop - heading.offset);
      if(pastHeading) {
        this.reset([pastHeading]);
      }
      onStickyCallback(heading, scrollPositionTop);
    },

    collision: function(fadeOutHeading, fadeInHeading, scrollPositionTop) {
      fadeOutHeading.node.addClass('sticky').css('top', fadeInHeading.offset - fadeOutHeading.offset - fadeOutHeading.height);
      fadeInHeading.node.addClass('sticky');
      onCollisionCallback(fadeOutHeading, fadeInHeading, scrollPositionTop);
    }
  }

  return function(selector) {

    var didResize = false;

    var headings;

    function mapHeadings() {
      headings = $(selector).map(function(i, e){
        var el = $(e);
        return { node: el, offset: el.offset().top, height: el.outerHeight()};
      });
    }

    mapHeadings();

    if(headings.length < 1) { return false; }

    function findPastHeadings(scrollPositionTop){
      var pastHeadings = [];
      $.each(headings, function(i, heading) {
        if (scrollPositionTop >= heading.offset) {
          pastHeadings.push(heading);
        }
      });
      return pastHeadings;
    }

    function onResize() {
      didResize = true;
    }

    function onScroll() {
      if(didResize) {
        mapHeadings();
        didResize = false;
      }
      layouter.reset(headings);
      var scrollPositionTop = $(window).scrollTop();
      var pastHeadings = findPastHeadings(scrollPositionTop);

      if (pastHeadings.length > 0) {
        var stickyHeading = pastHeadings[pastHeadings.length - 1];
        var nextHeading = headings[headings.index(stickyHeading) + 1];
        var pastHeading = null;
        if(pastHeadings.length > 1) {
          pastHeading = pastHeadings[pastHeadings.length - 2];
        }
        if (nextHeading && scrollPositionTop >= nextHeading.offset - stickyHeading.height) {
          layouter.collision(stickyHeading, nextHeading, scrollPositionTop);
        } else {
          layouter.sticky(stickyHeading, pastHeading, scrollPositionTop);
        }
      } else {
        layouter.noSticky(scrollPositionTop);
      }
    }

    $(window).scroll(onScroll);
    $(window).resize(onResize);

    return {

      onSticky: function(callback) {
        onStickyCallback = callback;
      },

      onNoSticky: function(callback) {
        onNoStickyCallback = callback;
      },

      onCollision: function(callback) {
        onCollisionCallback = callback;
      }

    }
  }
}(jQuery);
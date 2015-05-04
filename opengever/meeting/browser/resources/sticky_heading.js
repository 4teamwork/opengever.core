stickyHeading = function($){

  var onStickyCallback = function() {};
  var onNoStickyCallback = function() {};
  var onCollisionCallback = function() {};

  var clones = [];
  var headings;
  var doUpdate = false;

  var layouter = {
    reset: function(headings){
      $.each(headings, function(i, heading) { heading.clone.removeClass('sticky').css('top', 0); });
    },

    noSticky: function(scrollPositionTop){
      onNoStickyCallback(scrollPositionTop);
    },

    sticky: function(heading, pastHeading, scrollPositionTop){
      heading.clone.addClass('sticky');
      heading.clone.css('top', scrollPositionTop - heading.offset);
      if(pastHeading) {
        this.reset([pastHeading]);
      }
      onStickyCallback(heading, scrollPositionTop);
    },

    collision: function(fadeOutHeading, fadeInHeading, scrollPositionTop) {
      fadeOutHeading.clone.addClass('sticky').css('top', fadeInHeading.offset - fadeOutHeading.offset - fadeOutHeading.height);
      fadeInHeading.clone.addClass('sticky');
      onCollisionCallback(fadeOutHeading, fadeInHeading, scrollPositionTop);
    }
  }

  return function(selector) {

    var didResize = false;

    function init() {
      headings = $(selector).map(function(i, e){
        var el = $(e);
        var clone = el.clone();
        var height = el.outerHeight();
        var offset = el.offset().top;
        clone.attr("id", el.attr("id") + "_clone");
        el.addClass("original");
        clone.insertAfter(el);
        return { node: el, offset: offset, height: height, clone: clone};
      });
    }

    function update() {
      headings.each(function(i, e){
        e.offset = e.node.offset().top;
      });
    }

    init();

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

    function onScroll() {
      if(update) {
        update();
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

    return {

      onSticky: function(callback) {
        onStickyCallback = callback;
      },

      onNoSticky: function(callback) {
        onNoStickyCallback = callback;
      },

      onCollision: function(callback) {
        onCollisionCallback = callback;
      },

      doUpdate: function(value) {
        doUpdate = value;
      }

    }
  }
}(jQuery);
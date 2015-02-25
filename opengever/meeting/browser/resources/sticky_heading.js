stickyHeading = function($){
  var layouter = {
    reset: function(headings){
      $.each(headings, function(i, heading) { heading.node.removeClass('sticky').css('top', 0); });
    },

    noSticky: function(scrollPositionTop){
      // no-op
    },

    sticky: function(heading, scrollPositionTop){
      heading.node.addClass('sticky');
      heading.node.css('top', scrollPositionTop - heading.offset);
    },

    collision: function(fadeOutHeading, fadeInHeading, scrollPositionTop) {
      fadeOutHeading.node.addClass('sticky').css('top', fadeInHeading.offset - fadeOutHeading.offset - fadeOutHeading.height);
      fadeInHeading.node.addClass('sticky');
    }
  }

  return function(selector) {
    var headings = $(selector).map(function(i, e){
      var el = $(e);
      return { node: el, offset: el.offset().top, height: el.outerHeight()};
    });
    if(headings.length < 1) { return false; }

    function findStickyHeading(scrollPositionTop){
      var pastHeadings = [];
      $.each(headings, function(i, heading) {
        if (scrollPositionTop >= heading.offset) {
          pastHeadings.push(heading);
        }
      });
      return pastHeadings[pastHeadings.length - 1];
    }

    function onScroll() {
      layouter.reset(headings);
      var scrollPositionTop = $(window).scrollTop();
      var stickyHeading = findStickyHeading(scrollPositionTop);

      if (stickyHeading) {
        nextHeading = headings[headings.index(stickyHeading) + 1];
        if (nextHeading && scrollPositionTop >= nextHeading.offset - stickyHeading.height) {
          layouter.collision(stickyHeading, nextHeading, scrollPositionTop);
        } else {
          layouter.sticky(stickyHeading, scrollPositionTop);
        }
      } else {
        layouter.noSticky(scrollPositionTop);
      }
    }

    $(window).scroll(onScroll);
  }
}(jQuery);
(function(global, $) {

  function throttle(func) {
    return function () { requestAnimationFrame(func); };
  }

  if(!Array.prototype.last) {
    Array.prototype.last = function () {
      if(this.length) {
        return this[this.length - 1];
      }
    };
  }

  var $window = $(window);

  function PinItem(element, options) {

    options = $.extend({ pin: true }, options);

    element = $(element);

    var reveal = {};
    var offset = element.offset().top;
    var pushed = false;

    function top() { return position() - $window.scrollTop(); }

    function bottom() { return top() + height(); }

    function position() { return element.offset().top - $window.scrollTop(); }

    function height() { return element.innerHeight(); }

    function isPast() { return offset <= $window.scrollTop(); }

    function makeSticky(pushOffset) {
      element.addClass("pin-pinned");
      if(options.pin) {
        element.css("top", $window.scrollTop() - offset + pushOffset + "px");
      }
    }

    function pin(item) {
      var pushOffset = item ? item.height() : 0;
      makeSticky(pushOffset);
    }

    function pushedBy(item) {
      makeSticky(-(height() - item.position()));
    }

    function pushHeading(heading) {
      heading.makeSticky(-(heading.height() - position()));
    }

    function pushToolbar(toolbar) {
      toolbar.makeSticky(-(toolbar.height() - position()));
    }

    function release() {
      reveal.pushed = false;
      element.removeClass("pin-pinned");
      if(options.pin) {
        element.css("top", "auto");
      }
    }

    function refresh() {
      release();
      offset = element.offset().top;
    }

    function intersects(item) {
      return !(top() > item.bottom() || bottom() < item.top());
    }

    reveal.isPast = isPast;
    reveal.pin = pin;
    reveal.release = release;
    reveal.intersects = intersects;
    reveal.pushedBy = pushedBy;
    reveal.pushToolbar = pushToolbar;
    reveal.pushHeading = pushHeading;
    reveal.makeSticky = makeSticky;
    reveal.top = top;
    reveal.bottom = bottom;
    reveal.height = height;
    reveal.position = position;
    reveal.refresh = refresh;

    Object.defineProperty(reveal, "offset", { get: function() { return offset; } });
    Object.defineProperty(reveal, "element", { get: function() { return element; } });
    Object.defineProperty(reveal, "pushed", {
      get: function() { return pushed; },
      set: function(value) { pushed = value; }
    });

    return reveal;

  }

  function Heading(element, options) {

    var reveal = {};
    reveal.__proto__ = PinItem(element, options);

    function pushedBy(item){
      item.pushHeading(reveal);
    }

    reveal.pushedBy = pushedBy;

    return reveal;
  }

  function Toolbar(element, options) {

    var reveal = {};
    reveal.__proto__ = PinItem(element, options);

    function pushedBy(item){
      reveal.pushed = true;
      item.pushToolbar(reveal);
    }

    function pushHeading(heading) {
      if(!reveal.pushed) {
        reveal.pin(heading);
      }
    }

    reveal.pushedBy = pushedBy;
    reveal.pushHeading = pushHeading;

    return reveal;
  }

  function Pin(headings, toolbars, options) {

    options = $.extend({ pin: true }, options);

    var reveal = {};

    headings = $.map($(headings), function(heading) { return Heading(heading, options); });
    toolbars = $.map($(toolbars), function(toolbar) { return Toolbar(toolbar, options); });

    var items = headings.concat(toolbars);

    items.sort(function(left, right) { return left.offset - right.offset; });

    var pinCallback = $.noop;
    var releaseCallback = $.noop;

    function findPastItems(items) {
      return items.filter(function(item) {
        return item.isPast();
      });
    }

    function findCollidingItems(item, collidingItems) {
      collidingItems = collidingItems || [];
      var position = items.indexOf(item) + 1;
      var upcomingItems = items.slice(position);

      for(var i = 0; i < upcomingItems.length; i++) {
        var upcomingItem = upcomingItems[i];
        if(item.intersects(upcomingItem)) {
          collidingItems.push(upcomingItem);
          findCollidingItems(upcomingItem, collidingItems);
        } else {
          break;
        }
      }
      return collidingItems;
    }

    function findCollidingItemsInList(item, list) {
      return list.filter(function(listItem) {
        return item.intersects(listItem);
      });
    }

    function resetItems() { items.forEach(function(item) { item.release(); }); }

    function check() {
      resetItems();

      var pastItems = [];

      var pastHeadings = findPastItems(headings);
      var pastToolbars = findPastItems(toolbars);

      if(pastHeadings.length) {
        var topStickyHeading = pastHeadings.last();
        topStickyHeading.pin();
        pinCallback(topStickyHeading);
        pastItems.push(pastHeadings.last());

        if(pastToolbars.length) {
          var topStickyToolbar = pastToolbars.last();
          if(topStickyToolbar && topStickyToolbar.element.hasClass(topStickyHeading.element.attr("id"))) {
            topStickyToolbar.pin(topStickyHeading);
            pinCallback(topStickyToolbar);
            pastItems.push(pastToolbars.last());
          }
        }

      }

      if(pastItems.length) {
        var collidingItems = findCollidingItems(pastItems.last());

        collidingItems.forEach(function(item) {
             if(pastItems.indexOf(item) < 0) {
                 pastItems.push(item);
             }
        });

        pastItems = pastItems.reverse();
        pastItems.forEach(function(item, index) {
          var colliding = findCollidingItemsInList(item, pastItems.slice(index+1));
          colliding.forEach(function(collidingItem) {
            collidingItem.pushedBy(item);
          });
        });

      } else {
        releaseCallback();
      }

    }

    function refresh() {
      items.forEach(function(item) { item.refresh(); });
      check();
    }

    function onPin(callback) { pinCallback = callback; }

    function onRelease(callback) { releaseCallback = callback; }

    $window.on("resize", throttle(function() {
      refresh();
      check();
    }));

    $window.on("scroll", throttle(check));

    check();

    reveal.onPin = onPin;
    reveal.onRelease = onRelease;
    reveal.refresh = refresh;

    return Object.freeze(reveal);

  }

  window.Pin = Pin;

})(window, window.jQuery);

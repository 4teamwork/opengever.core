(function(global, $) {

  "use strict";

  function Scrollspy(target) {

    target = $(target);

    var element = target.parent();

    var reveal = {};

    var anchors = $("a", target);

    var beforeSelectCallback = $.noop;

    var root = $("html, body");

    function scrollTo(offset, callback) { root.animate({ scrollTop: offset + "px" }, 300, callback); }

    function extractAnchor(node) {
      node = $(node);
      return $(node.attr("href"));
    }

    function applyAnchor(node) {
      var anchor = extractAnchor(node);
      scrollTo(anchor.offset().top + 1);
    }

    function expand(node) {
      var expandable = node.next(".expandable");
      if(!expandable.length) {
        return false;
      }
      $(".expanded").removeClass("expanded");
      expandable.addClass("expanded");
      expandable.prev().addClass("selected");
    }

    function select(node) {
      node = $(node);
      beforeSelectCallback(node, extractAnchor(node));
      node.closest("ul").find(".selected").removeClass("selected");
      node.addClass("selected");
      expand(node);
    }

    function onSelect(callback) { beforeSelectCallback = callback; }

    function reset() {
      $(".selected").removeClass("selected");
      $(".expanded").removeClass("expanded");
    }

    function releaseScroll() { $(window).off("wheel"); }

    function trapScroll(range) {
      $(window).on("wheel", function(event) {
        var deltaY = event.originalEvent.deltaY;
        var offset = element.scrollTop();
        if ((deltaY > 0 && offset >= range) || (deltaY < 0 && offset <= 0)) {
          event.preventDefault();
        }
      });
    }

    anchors.on("click", function(event) {
      event.preventDefault();
      applyAnchor(event.currentTarget);
    });

    element.on("mouseover", function() {
      var range = element.children("ul").height() - element.height();
      trapScroll(range);
    });
    element.on("mouseleave", function() { releaseScroll(); });

    reveal.select = select;
    reveal.onSelect = onSelect;
    reveal.reset = reset;

    return Object.freeze(reveal);

  }

  global.Scrollspy = Scrollspy;

}(window, jQuery));

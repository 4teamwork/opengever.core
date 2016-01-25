(function(global, $) {

  "use strict";

  function Scrollspy(_options) {

    this.options = $.extend({
      selector: "",
      offset: 0,
      animationSpeed: 300,
      scrollOffset: 100
    }, _options || {});

    var scrollCallback = function() {};

    var beforeScrollCallback = function() {};

    var root = $("html, body");

    var self = this;

    this.element = $(this.options.selector);

    this.init = function() {
      $("a", this.element).click(function(event) {
        event.preventDefault();
        var target = $(event.currentTarget);
        self.applyAnchor(target);
      });
      this.element.on("mouseover", function() {
        var range = self.element.children("ul").height() - self.element.height();
        self.trapScroll(range);
      });
      this.element.on("mouseleave", function() { self.releaseScroll(); });
    };

    this.trapScroll = function(range) {
      $(window).on("wheel", function(event) {
        var deltaY = event.originalEvent.deltaY;
        var offset = self.element.scrollTop();
        if ((deltaY > 0 && offset >= range) || (deltaY < 0 && offset <= 0)) {
          event.preventDefault();
        }
      });
    };

    this.releaseScroll = function() { $(window).off("wheel"); };

    this.align = function() {
      var selected = $(".selected", this.element);
      var offset = 0;
      if(selected.length) {
        offset = selected.offset().top - this.element.offset().top + this.element.scrollTop() - this.options.scrollOffset;
      }
      $(this.element).stop().animate({ scrollTop: offset + "px" }, this.options.animationSpeed);
    };

    this.expand = function(target) {
      if(target.hasClass("expandable")) {
        $(".expandable", this.element).not(target).removeClass("expanded");
        target.addClass("expanded");
      }
    };

    this.scrollTo = function(offset, callback) {
      offset = offset - this.options.offset;
      root.animate({ scrollTop: offset + "px" }, this.options.animationSpeed, callback);
    };

    this.extractAnchor = function(target) {
      return $(target.attr("href"));
    };

    this.applyAnchor = function(target) {
      var anchor;
      if (target.hasClass("expandable")) {
        anchor = this.extractAnchor(target.next().find(".field").first());
      } else if(target.hasClass("paragraph")) {
        anchor = this.extractAnchor(target.parent().next().find(".field").first());
      }
      else {
        anchor = this.extractAnchor(target);
      }
      beforeScrollCallback(target, anchor);
      this.scrollTo(anchor.offset().top, function() { scrollCallback(target, anchor); });
    };

    this.select = function(target) {
      var selected = $(".selected", this.element).not(target);
      selected.removeClass("selected");
      target.addClass("selected");
      var parent = target.closest("ul").prev(".expandable");
      selected.not(parent).removeClass("selected");
      parent.addClass("selected");
      this.align();
    };

    this.reset = function() {
      $(".selected", this.element).removeClass("selected");
      $(".expanded", this.element).removeClass("expanded");
    };

    this.onBeforeScroll = function(callback) { beforeScrollCallback = callback; };

    this.onScroll = function(callback) { scrollCallback = callback; };

    this.init();
  }

  global.Scrollspy = Scrollspy;

}(window, jQuery));

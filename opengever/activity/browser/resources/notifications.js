(function(global, $, HBS) {

  "use strict";

  var Notifications = function(options) {

    options = $.extend({
      template: "",
      outlet: "",
      read: "",
      scrollOffset: 300
    }, options || {});

    options.template = HBS.compile(options.template);

    var self = this;

    this.appendItems = function(items) {
      options.outlet.append(items);
      $(".timeago", options.outlet).timeago();
    };

    this.listItems = function(data) {
      self.nextUrl = data.next_page;
      var items = options.template({ notifications: data.notifications });
      self.appendItems(items);
    };

    this.list = function(endpoint) { $.get(endpoint).done(this.listItems); };

    this.next = function() {
      options.outlet.off("scroll");
      if(this.nextUrl) {
        this.list(this.nextUrl);
      }
    };

    this.updateCount = function(count) {
      var counter = $(".unread_number");
      var currentCount = parseInt(counter.html());
      var newCount = currentCount - count;
      if(newCount) {
        counter.html(newCount);
      } else {
        counter.remove();
      }
      options.outlet.off("scroll").on("scroll", this.trackScroll);
    };

    this.trackScroll = function() {
      var menuHeight = 0;
      $(this).children(".notification-item").each(function() {
        menuHeight += $(this).outerHeight();
      });
      if($(this).scrollTop() + $(this).height() >= menuHeight - options.scrollOffset) {
        self.next();
      }
    };

  };

  global.Notifications = Notifications;

  var initNotifications = function() {
    var template = $("#notificationTemplate").html();
    var endpoints = $("#portal-notifications dl.notificationsMenu").data();
    var outlet = $(".notifications");
    var notifications = new Notifications({
      template: template,
      outlet: outlet,
      update: endpoints.readUrl
    });
    $(".notificationsMenuHeader > a").on("click", function(event) {
      event.preventDefault();
      toggleMenuHandler.call(this, event);
      if($(this).parents(".notificationsMenu").hasClass("activated")) {
        outlet.empty();
        notifications.list(endpoints.listUrl);
      }
    });
    $(".read-all-notifications").on("click", function(event) {
      event.preventDefault();
      var postReadAll = $.post(endpoints.readUrl, { "timestamp": Math.round(new Date().getTime()/1000) });
      $.when(postReadAll.success()).then(function(){
        var counter = $(".unread_number");
        counter.remove();
      });
    });
  };

  $(function(){
    if($('#portal-notifications-selector-menu').length){
      initNotifications();
    }
  });

}(window, jQuery, window.Handlebars));

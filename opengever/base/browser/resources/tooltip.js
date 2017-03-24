(function(global, $) {

  "use strict";

  var settings = {
    overwrite: false, // Do not reload the tooltip when it's already created
    content: { text: tooltipContent }, // Set ajax content
    position: {
      target: "mouse", // Set tooltip position relative to the current mouse location
      viewport: $(window), // The tooltip must not leave the window
      at: "bottom right",
      my: "center left",
      adjust: {
        mouse: false, // Do not track the mouse
        x: 20, // Slighly shift the location in x direction
        y: 20 // Slighly shift the location in y direction
      },
      effect: false // Do not animate the tooltip loaction changes
    },
    show: {
      solo: true, // Make sure that only one tooltip is visible
      effect: false, // Show the tooltip immediately
      ready: true, // Make sure that the tooltip gets shown immediately when it's ready
      delay: 300 // The tooltip gets shown after 300ms
    },
    hide: {
      delay: 300, // The tooltip gets hidden after 300ms
      effect: false, // Hide the tooltip immediately
      fixed: true // Make sure the tooltip gets not hidden if mouse is over the tooltip
    },
    events: {
      show: closeTooltips,
      hide: destroyTooltips,
    }
  };

  function spinner() { return '<img src="' + $("head > base").attr("href") + '/spinner.gif" class="spinner"/>'; }

  function failure(status, error) { return status + ": " + error; }

  function tooltipContent(event, api) {
    $.get($(event.currentTarget).data("tooltip-url"))
      .done(function(data) {
        api.set("content.text", data);
        $(document).trigger("tooltip.show", [api]);
        $(".showroom-reference").on("click", function() { api.hide(); });
      })
      .fail(function(xhr, status, error) { api.set("content.text", failure(status, error)); });
    return spinner();
  }

  function initTooltips(event) { $(event.currentTarget).qtip(settings, event); }

  function closeTooltips(event, api) { $(event.originalEvent.target).on("click", function() { api.hide(); }); }

  function destroyTooltips(event, api) { api.destroy(true); }

  $(document).on("mouseover", ".tooltip-trigger", initTooltips);

}(window, window.jQuery));


(function(global, $) {

  "use strict";

  function setBreadcrumbAsTitleAttr(event) {
    var target = $(event.currentTarget);
    var title = target.attr('title');
    if ((typeof title !== typeof undefined && title !== false)){
      return;
    }

    setTimeout(function(){
      if (!target.is(":hover")){
        return;
      }

      $.get(portal_url + '/breadcrumb_by_uid', {ploneuid: target.data("uid")}).done(function(data){
        target.attr('title', data);
        // Force the browser to repaint - otherwise the tooltip is not directly displayed
        target.hide(0);
        target.show(0);
      });
    }, 100);
  }

  $(document).on("mouseover", ".rollover-breadcrumb[data-uid]", setBreadcrumbAsTitleAttr);


}(window, window.jQuery));

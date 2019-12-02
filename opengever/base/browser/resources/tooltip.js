(function(global, $) {

  "use strict";

  var tooltipHideTimer = null;
  var viewingDocument = false;

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
        x: 20, // Slightly shift the location in x direction
        y: 20 // Slightly shift the location in y direction
      },
      effect: false // Do not animate the tooltip location changes
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
      hide: hideBackdrop,
    }
  };

  function spinner() { return '<img src="' + $("head > base").attr("href") + '/spinner.gif" class="spinner"/>'; }

  function isTooltipResponse(data, status, jqXHR) {
    if(jqXHR.getResponseHeader('X-Tooltip-Response') !== "True") {
      return $.Deferred().reject(jqXHR, "X-Tooltip-Response missing on tooltip response.");
    }
    return $.Deferred().resolve(data, status, jqXHR);
  }

  function tooltipContent(event, api) {
    $.get($(event.currentTarget).data("tooltip-url"))
      .pipe(isTooltipResponse)
      .done(function(data) {
        api.set("content.text", data);
        $(document).trigger("tooltip.show", [api]);
        $(".showroom-reference").on("click", function() { api.hide(); });
      })
      .fail(function() {
        // Avoid cancelling a pending navigation request initiated by the user
        if (!viewingDocument) {
          location.reload();
        }
      });
    return spinner();
  }

  function initTooltips(event) { $(event.currentTarget).qtip(settings, event); }

  function activateTableCell(target) {
    $(target).closest('.x-grid3-row').addClass('bumblebee-tooltip-active');
  }

  function deactivateOtherTableCells(target) {
    $(target).closest('.x-grid3-row').siblings().removeClass('bumblebee-tooltip-active');
  }

  function deactivateActiveTableCells() {
    $('body .bumblebee-tooltip-active').removeClass('bumblebee-tooltip-active');
  }

  function showBackdrop(event) {
    var target = event.originalEvent.target;
    deactivateOtherTableCells(target);
    clearTimeout(tooltipHideTimer);
    $('body').addClass('bumblebee-tooltip-open');
    activateTableCell(target);
  }

  function hideBackdrop(event) {
    tooltipHideTimer = setTimeout(function() {
      $('body').removeClass('bumblebee-tooltip-open');
      deactivateActiveTableCells();
    }, settings.hide.delay / 2);
  }

  function closeTooltips(event, api) {
    var target = event.originalEvent.target;
    $(target).on("click", function() {
      viewingDocument = true;
      api.hide();
      hideBackdrop(event);
    });
    showBackdrop(event);
  }

  var hasTouched = false;

  $(document).on("touchstart", ".tooltip-trigger", function() {
    hasTouched = true;
  });
  $(document).on("mouseover", ".tooltip-trigger", function(e) {
    if (hasTouched) { return; }
    initTooltips(e);
  });

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

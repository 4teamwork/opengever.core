(function(global, Showroom, $) {

  var endpoint;
  var showroom;
  var numberOfDocuments;

  function scanForBrokenImages(context) {
    $("img", context).error(function(){
      $(this)
        .attr("src", "++resource++opengever.bumblebee.resources/fallback.svg")
        .addClass("broken-image");
    });
  }

  function loadNextTabbedviewItems() {
    var data = {
      documentPointer: $('.imageContainer').length,
      searchableText: global.tabbedview.searchbox.val()
    };
    $.get(endpoint, data).done(function(data) {
      var items = $(data).filter('.imageContainer');
      items.insertAfter($('.imageContainer').last());
      toggleShowMoreButton();
      showroom.append(items);
      scanForBrokenImages(items);
    });
  }


  function toggleShowMoreButton() {
    var button = $('.bumblebeeGalleryShowMore');
    var shown = $('.imageContainer').length;

    if (shown >= numberOfDocuments) {
      button.hide();
    } else {
      button.css("display", "block");
    }
  }

  function tail(item) {
    if(global.tabbedview) {
      loadNextTabbedviewItems();
    }
  }

  function init() {
    showroom = Showroom([], { 'tail': tail });
    updateShowroom();

    // The search.js does not trigger an event after reloading the searchview.
    // The only possiblity to update the showroom is to listen on the ajaxComplete
    // event which will be triggered after every ajax request.
    //
    // First we have to check if we are really on the search-site to register
    // the event-listener.
    //
    // If the event have been triggered, it is possible that it has been triggered
    // by the showroom itself. If we do an updateShowroom while the overlay is open,
    // we will destroy it. So we have to do this check first before updating
    // the showroom.
    if ($('#search-results').length) {
      $( document ).ajaxComplete(function(event, jqXHR, params) {
        if(params.url.indexOf("@@updated_search") !== -1) {
          updateShowroom();
        }
      });
    }
  }

  function getNumberOfDocuments(fallback_value) {
    var galleryDocuments = $(".preview-listing").data('number-of-documents')

    if ( $.isNumeric(galleryDocuments) ) {
      // we are in gallery_view
      return galleryDocuments;
    }

    if ( window.store ) {
      // The store-attribute comes from ftw.table. If it's available,
      // we are on a list view.
      var listDocuments = store.totalLength
      if ( $.isNumeric(listDocuments)) {
        return listDocuments;
      }
    }
    // we are somewhere else i.e. search view
    return fallback_value;
  }

  function updateShowroom() {
    var items = document.querySelectorAll(".showroom-item");
    var previewListing = $(".preview-listing");

    endpoint = previewListing.data("fetch-url");
    numberOfDocuments = getNumberOfDocuments(fallback_value=items.length);
    toggleShowMoreButton();
    scanForBrokenImages(".preview-listing");

    showroom.reset(items);
    showroom.setTotal(numberOfDocuments);
  }

  $(document)
    .on("reload", updateShowroom)
    .on("viewReady", updateShowroom)
    .on("click", ".bumblebeeGalleryShowMore", function() {loadNextTabbedviewItems(); });
  $(init);

})(window, window.showroom, window.jQuery);

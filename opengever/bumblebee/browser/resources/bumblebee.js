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

  function extendShowroomQueue(pagenumber, extender){
    var fetch_url = store.proxy.url.split('?')[0]
    var params = {'pagenumber': pagenumber,
                  'initialize': 0,
                  'view_name': global.tabbedview.prop('view_name'),
                  'tableType': 'extjs'}

    $.get(fetch_url, params).done(function(data){
      extender(data.rows.map(function(row) {
        return $(row['sortable_title']).children("a.showroom-item")[0];
      }));
    });

  }

  function loadNextListingItems() {
    var pagenumber = global.tabbedview.param('pagenumber:int') || 1;
    extendShowroomQueue(pagenumber + 1, showroom.append);
  }

  function loadPreviousListingItems() {
    var pagenumber = global.tabbedview.param('pagenumber:int');
    if (!pagenumber) {
      // If there is no pagenumber given, the listing shows the first page,
      // so there are no previous items.
      return
    }
    extendShowroomQueue(pagenumber - 1, showroom.prepend);
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

  function tail() {
    if(global.tabbedview) {
      if (global.tabbedview.table.length) {
        // document table listing
        loadNextListingItems();
      }
      loadNextTabbedviewItems();
    }
  }

  function head() {
    if(global.tabbedview && global.tabbedview.table.length) {
      // document table listing
      loadPreviousListingItems();
    }
  }

  function init() {
    showroom = Showroom([], { 'tail': tail, 'head': head });
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
          initSingleShowroom();
        }
      });
    }
  }

  function getNumberOfDocuments(fallback_value) {
    var galleryDocuments = $(".preview-listing").data('number-of-documents');

    if ( $.isNumeric(galleryDocuments) ) {
      // we are in gallery_view
      return galleryDocuments;
    }

    if ( window.store ) {
      // The store-attribute comes from ftw.table. If it's available,
      // we are on a list view.
      var listDocuments = window.store.totalLength;
      if ( $.isNumeric(listDocuments)) {
        return listDocuments;
      }
    }
    // we are somewhere else i.e. search view
    return fallback_value;
  }

  function getOffset() {
    if ( window.store ) {
      // The store-attribute comes from ftw.table. If it's available,
      // we are on a list view.
      var pagenumber = global.tabbedview.param('pagenumber:int') || 1;
      var batchSize = $('#tabbedview-batchbox').val();
      if ( batchSize && pagenumber > 1) {
        return (pagenumber - 1) * batchSize;
      }
    }
    return 0;

  }

  function updateShowroom() {
    if(($(".template-search").length)) {
      initSingleShowroom();
      return;
    }
    var items = document.querySelectorAll(".showroom-item");
    var previewListing = $(".preview-listing");

    endpoint = previewListing.data("fetch-url");
    numberOfDocuments = getNumberOfDocuments(items.length);
    toggleShowMoreButton();
    scanForBrokenImages(".preview-listing");

    showroom.reset(items, getOffset());
    showroom.setTotal(numberOfDocuments);
  }

  function initSingleShowroom() {
    var items = [].slice.call(document.querySelectorAll(".showroom-item"));
    var previewListing = $(".preview-listing");

    endpoint = previewListing.data("fetch-url");
    scanForBrokenImages(".preview-listing");
    items.forEach(function(item) {
      Showroom([item], { displayCurrent: false });
    });
  }

  $(document)
    .on("reload", updateShowroom)
    .on("viewReady", updateShowroom)
    .on("agendaItemsReady", updateShowroom)
    .on("click", ".bumblebeeGalleryShowMore", function() {loadNextTabbedviewItems(); });
  $(init);

})(window, window.showroom, window.jQuery);

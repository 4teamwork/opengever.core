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

  function loadNextTabbedviewGalleryView() {
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

  function extendTabbedviewTableShowroomItems(pagenumber, extender) {
    var fetch_url = store.proxy.url.split('?')[0];
    var params = {'pagenumber': pagenumber,
                  'initialize': 0,
                  'view_name': global.tabbedview.prop('view_name'),
                  'tableType': 'extjs'};

    $.get(fetch_url, params).done(function(data) {
      extender(data.rows.map(function(row) {
        return $(row['sortable_title']).children("a.showroom-item")[0];
      }));
    });

  }

  function loadNextTabbedviewTableItems() {
    var pagenumber = global.tabbedview.param('pagenumber:int') || 1;
    extendTabbedviewTableShowroomItems(pagenumber + 1, showroom.append);
  }

  function loadPreviousTabbedviewTableItems() {
    var pagenumber = global.tabbedview.param('pagenumber:int');
    if (!pagenumber) {
      // If there is no pagenumber given, the listing shows the first page,
      // so there are no previous items.
      return;
    }
    extendTabbedviewTableShowroomItems(pagenumber - 1, showroom.prepend);
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
    if (isOnTabbedviewGalleryView()) {
      loadNextTabbedviewGalleryView();
    }

    else if (isOnTabbedviewTableView()) {
      loadNextTabbedviewTableItems();
    }
  }

  function head() {
    if (isOnTabbedviewTableView) {
      loadPreviousTabbedviewTableItems();
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
    if (isOnSearchView()) {
      $( document ).ajaxComplete(function(event, jqXHR, params) {
        if(params.url.indexOf("@@updated_search") !== -1) {
          updateShowroom();
        }
      });
    }
  }

  function getNumberOfDocuments(fallback_value) {
    var galleryDocuments = $(".preview-listing").data('number-of-documents');

    if ($.isNumeric(galleryDocuments)) {
      // we are in gallery_view
      return galleryDocuments;
    }

    else if (isOnTabbedviewTableView()) {
      var listDocuments = window.store.totalLength;
      if ($.isNumeric(listDocuments)) {
        return listDocuments;
      }
    }

    else if (isOnSearchView()) {
      searchResultsNumber = $('#search-results-number').text();
      if ($.isNumeric(searchResultsNumber)) {
        return parseInt(searchResultsNumber);
      }
    }
    // we are somewhere else i.e. search view
    return fallback_value;
  }

  function getOffset() {
    if (isOnTabbedviewTableView()) {
      var pagenumber = global.tabbedview.param('pagenumber:int') || 1;
      var batchSize = $('#tabbedview-batchbox').val();
      if (batchSize && pagenumber > 1) {
        return (pagenumber - 1) * batchSize;
      }
    }

    else if (isOnSearchView()) {
      offset = parseQueryString('b_start');
      if ($.isNumeric(offset)) {
        return parseInt(offset);
      }

    }
    return 0;

  }

  function isOnSearchView() {
    // If the search-results tag is available, we are on the search-view.
    return $('#search-results').length;
  }

  function isOnTabbedviewTableView() {
    // The store-attribute comes from ftw.table. If it's available,
    // we are on a list view.
    return window.store;
  }

  function isOnTabbedviewGalleryView() {
    return $('.preview-listing').length;
  }

  function parseQueryString(name) {
    // Returns the value of a url-parameter.
    return window.location.search.split(/&/).filter(function(pair) {
      return pair.indexOf(name) >= 0;
    }).map(function(pair) {
      return pair.split("=")[1];
    }).join();
  }

  function updateShowroom() {
    var items = document.querySelectorAll(".showroom-item");
    var previewListing = $(".preview-listing");

    endpoint = previewListing.data("fetch-url");
    numberOfDocuments = getNumberOfDocuments(items.length);
    toggleShowMoreButton();
    scanForBrokenImages(".preview-listing");

    showroom.reset(items, getOffset());
    showroom.setTotal(numberOfDocuments);
    showroom.refresh();
  }

  $(document)
    .on("reload", updateShowroom)
    .on("viewReady", updateShowroom)
    .on("agendaItemsReady", updateShowroom)
    .on("click", ".bumblebeeGalleryShowMore", function() {loadNextTabbedviewGalleryView(); });
  $(init);

})(window, window.showroom, window.jQuery);

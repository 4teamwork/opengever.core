(function(global, Showroom, $) {

  var endpoint;
  var showroom;
  var numberOfDocuments;

  var template = (' \
    <div class="{{showroom.options.cssClass}}"> \
      <div class="ftw-showroom-backdrop"></div> \
      <nav> \
        <a id="ftw-showroom-prev" class="ftw-showroom-button"></a> \
        {{#if showroom.options.displayCurrent}} \
          <span class="ftw-showroom-current">{{showroom.current}}</span> \
        {{/if}} \
        {{#if showroom.options.displayTotal}} \
          {{#if showroom.options.total}}<span>/</span> \
            <span class="ftw-showroom-total">{{showroom.options.total}}</span> \
          {{/if}} \
        {{/if}} \
        <a id="ftw-showroom-next" class="ftw-showroom-button"></a> \
        <a id="ftw-showroom-close" class="ftw-showroom-button"></a> \
      </nav> \
      {{{content}}} \
    </div> \
  ');

  function scanForBrokenImages(context) {
    $("img", context).error(function(){
      $(this)
        .attr("src", "++resource++opengever.bumblebee.resources/fallback.svg")
        .addClass("broken-image");
    });
  }

  function loadNextTabbedviewGalleryView() {
    var data = {
      documentPointer: $(".imageContainer").length,
      searchableText: global.tabbedview.searchbox.val()
    };
    $.get(endpoint, data).done(function(data) {
      var items = $(data).filter(".imageContainer");
      items.insertAfter($(".imageContainer").last());
      toggleShowMoreButton();
      showroom.append(items);
      scanForBrokenImages(items);
    });
  }

  function fetchTabbedviewTableShowroomItems(pagenumber) {
    var fetch_url = global.store.proxy.url.split("?")[0];
    var params = {"pagenumber": pagenumber,
                  "initialize": 0,
                  "view_name": global.tabbedview.prop("view_name"),
                  "tableType": "extjs"};

    return $.get(fetch_url, params);
  }

  function convertTabbedviewTableAjaxRowsToShowroomItems(tabledata) {
    return tabledata.rows.map(function(row) {
      return $(row.sortable_title).children("a.showroom-item")[0];
    });
  }

  function loadNextTabbedviewTableItems() {
    var pagenumber = getTabbedviewTablePagenumber();
    fetchTabbedviewTableShowroomItems(pagenumber + 1).done(function(data) {
      showroom.append(convertTabbedviewTableAjaxRowsToShowroomItems(data));
    });

  }

  function loadPreviousTabbedviewTableItems() {
    var pagenumber = getTabbedviewTablePagenumber();
    if (!pagenumber) {
      // If there is no pagenumber given, the listing shows the first page,
      // so there are no previous items.
      return;
    }
    fetchTabbedviewTableShowroomItems(pagenumber - 1).done(function(data) {
      showroom.prepend(convertTabbedviewTableAjaxRowsToShowroomItems(data));
    });
  }

  function fetchSearchViewItems(fetchurl) {
    if (!fetchurl) { return; }

    var parser = document.createElement("a");
    parser.href = fetchurl;

    var queryString = parser.search;

    // In order to update the showroom items after changing the search-query
    // trough the web, we had to register an event-listener for the
    // updated_search-view (see init-Method in this file).
    //
    // We have to do the same ajax-request here but don"t want to update the
    // showroom. For this case we have to deactivate the event-listerer
    // by adding a special request-parameter which will be handled in the
    // event-listener.
    var additionalParams = {"deactivate_update": true};

    return $.get("@@updated_search" + queryString, additionalParams);
  }

  function loadNextSearchItems() {
    var url = $("#search-results .pagination .next").attr("href");
    if (!url) { return; }

    fetchSearchViewItems(url).done(function(data) {
      showroom.append($(".showroom-item", data));
    });
  }

  function loadPreviousSearchItems() {
    var url = $("#search-results .pagination .previous").attr("href");
    if (!url) { return; }

    fetchSearchViewItems(url).done(function(data) {
      showroom.prepend($(".showroom-item", data));
    });
  }

  function toggleShowMoreButton() {
    var button = $(".bumblebeeGalleryShowMore");
    var shown = $(".imageContainer").length;

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

    else if (isOnSearchView()) {
      loadNextSearchItems();
    }
  }

  function head() {
    if (isOnTabbedviewTableView()) {
      loadPreviousTabbedviewTableItems();
    }

    else if (isOnSearchView()) {
      loadPreviousSearchItems();
    }
  }

  function init() {
    showroom = Showroom([], {
      "tail": tail,
      "head": head,
      template: template
    });
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
    //
    // It"s also possible to deactivate this listener by adding a "deactivate_update"
    // request parameter.
    if (isOnSearchView()) {
      $(document).ajaxComplete(function(event, jqXHR, params) {
        if (params.url.indexOf("@@updated_search") !== -1 &&
            params.url.indexOf("deactivate_update=true") === -1) {

          updateShowroom();
        }

      });
    }
  }

  function getNumberOfDocuments(fallbackValue) {
    var galleryDocuments = $(".preview-listing").data("number-of-documents");

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
      var searchResultsNumber = $("#search-results .searchResults").data("number-of-documents");
      if ($.isNumeric(searchResultsNumber)) {
        return parseInt(searchResultsNumber, 10);
      }
    }
    // we are somewhere else i.e. search view
    return fallbackValue;
  }

  function getTabbedviewTablePagenumber() {
    return global.tabbedview.param("pagenumber:int") || 1;
  }

  function getOffset() {
    if (isOnTabbedviewTableView()) {
      var pagenumber = getTabbedviewTablePagenumber();
      var batchSize = parseInt($("#tabbedview-batchbox").val(), 10);
      if (batchSize && pagenumber) {
        return (pagenumber - 1) * batchSize;
      }
    }

    else if (isOnSearchView()) {
      var offset = $("#search-results .searchResults").data("offset");
      if ($.isNumeric(offset)) {
        return parseInt(offset, 10);
      }

    }
    return 0;

  }

  function isOnSearchView() {
    // If the search-results tag is available, we are on the search-view.
    return $("#search-results").length;
  }

  function isOnTabbedviewTableView() {
    // The store-attribute comes from ftw.table. If it"s available,
    // we are on a list view.
    return window.store;
  }

  function isOnTabbedviewGalleryView() {
    return $(".preview-listing").length;
  }

  function closeShowroom() { showroom.close(); }

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
    .on("click", ".bumblebeeGalleryShowMore", loadNextTabbedviewGalleryView)
    .on("click", ".ftw-showroom-backdrop", closeShowroom);
  $(init);

})(window, window.showroom, window.jQuery);

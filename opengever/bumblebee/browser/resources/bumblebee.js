(function(global, Showroom, $) {

  var endpoint;
  var showroom;
  var numberOfDocuments;

  var searchViewNavigationBatch = {
    batchSize: 0,
    batchStartNext: 0,
    batchStartPrevious: 0,
    batchURLNext: "",
    batchURLPrevious: "",
    initBatchPosition: function(batchSize, offset, nextURL, previousURL) {
      this.batchSize = batchSize;
      this.batchStartNext = offset + batchSize;
      this.batchStartPrevious = offset - batchSize;
      this.batchURLNext = nextURL;
      this.batchURLPrevious = previousURL;
    },
    getNextBatchURL: function() {
      var url = this.generateURL(this.batchURLNext, this.batchStartNext);
      this.batchStartNext += this.batchSize;
      return url;
    },
    getPrevBatchURL: function() {
      if (this.batchStartPrevious < 0) { return; }
      var url = this.generateURL(this.batchURLPrevious, this.batchStartPrevious);
      this.batchStartPrevious -= this.batchSize;
      return url;
    },
    generateURL: function(url, b_start) {
      if (!url) { return; }
      return url.replace(/(b_start:int=)\d+(&)/, "$1" + b_start + "$2");
    }
  };
  var template = (' \
    <div class="{{showroom.options.cssClass}} {{#if showroom.options.isMenuOpen}}menu-open{{/if}}"> \
      <header class="ftw-showroom-header"> \
        <h1><span class="{{item.mimeType}}"></span>{{item.title}}</h1> \
        <nav> \
          <a class="ftw-showroom-button ftw-showroom-prev"></a> \
          {{#if showroom.options.multiple}} \
            <div class="ftw-showroom-header-tile ftw-showroom-pagecount"> \
              {{#if showroom.options.displayCurrent}} \
                <span class="ftw-showroom-current">{{showroom.current}}</span> \
              {{/if}} \
              {{#if showroom.options.displayTotal}} \
                {{#if showroom.options.total}}<span>/</span> \
                  <span class="ftw-showroom-total">{{showroom.options.total}}</span> \
                {{/if}} \
              {{/if}} \
            </div> \
          {{/if}} \
          <a class="ftw-showroom-button ftw-showroom-next"></a> \
          <a id="ftw-showroom-menu" class="ftw-showroom-button {{#if showroom.options.isMenuOpen}}selected{{/if}}"></a> \
          <a class="ftw-showroom-button ftw-showroom-close"></a> \
        </nav> \
      </header> \
      {{{content}}} \
    </div> \
  ');

  function scanForBrokenImages(context) {
    $(context).error(function(){
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
      scanForBrokenImages(".bumblebee-thumbnail");
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
    if (pagenumber === 1) {
      // We don't need to fetch previous elements if we are on the first page
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
    var url = searchViewNavigationBatch.getNextBatchURL();
    if (!url) { return; }

    fetchSearchViewItems(url).done(function(data) {
      showroom.append($(".showroom-item", data));
    });
  }

  function loadPreviousSearchItems() {
    var url = searchViewNavigationBatch.getPrevBatchURL();
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

  function getMimeType() {
    return $(".metadata").data("mimetype")
  }

  function init() {
    showroom = Showroom([], {
      tail: tail,
      head: head,
      template: template,
      isMenuOpen: true,
      beforeRender: function(item, content) {
        item.mimeType = $(".metadata", content).data("mimetype");
      }
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
          BumblebeeCable.gatherNodes();
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
      var batchSize = parseInt($(".tabbedviewBatchbox").first().val(), 10);
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
    scanForBrokenImages(".bumblebee-thumbnail, .documentPreview > img");

    showroom.reset(items, getOffset());
    showroom.setTotal(numberOfDocuments);
    showroom.options.multiple = numberOfDocuments > 1

    if (isOnSearchView()) {
      showroom.options.multiple = false;
      searchViewNavigationBatch.initBatchPosition(
        $("#search-results").data("batch-size"),
        getOffset(),
        $("#search-results .pagination .next").attr("href"),
        $("#search-results .pagination .previous").attr("href")
        );
    }

  }

  function toggleMenu() {
    showroom.options.isMenuOpen = !showroom.options.isMenuOpen;
    $(this).toggleClass("selected");
    showroom.element.toggleClass("menu-open");
  }

  $(document)
    .on("reload", function() {
      BumblebeeCable.gatherNodes();
      updateShowroom();
    })
    .on("ready", function() {
      BumblebeeCable.init(window.bumblebee_notification_url);
    })
    .on("tooltip.show", function() {
      scanForBrokenImages(".bumblebee-thumbnail");
      BumblebeeCable.gatherNodes();
    })
    .on("showroom:item:shown", BumblebeeCable.gatherNodes)
    .on("viewReady", function() {
      BumblebeeCable.gatherNodes();
      updateShowroom();
    })
    .on("agendaItemsReady", updateShowroom)
    .on("click", ".bumblebeeGalleryShowMore", loadNextTabbedviewGalleryView)
    .on("click", "#ftw-showroom-menu", toggleMenu);
  $(init);

})(window, window.ftw.showroom, window.jQuery);

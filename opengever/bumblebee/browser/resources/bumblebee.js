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
  }

  function updateShowroom() {
    var items = document.querySelectorAll(".showroom-item");
    var previewListing = $(".preview-listing");

    endpoint = previewListing.data("fetch-url");
    numberOfDocuments = previewListing.data('number-of-documents') || items.length;
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

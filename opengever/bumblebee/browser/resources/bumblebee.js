(function(global, Showroom, $) {

  var endpoint;
  var showroom;
  var number_of_documents;

  function scanForBrokenImages(context) {
    $("img", context).error(function(){
      $(this)
        .attr("src", "++resource++opengever.bumblebee.resources/fallback.svg")
        .addClass("broken-image");
    });
  }

  function loadNextItems() {
    var data = { document_pointer: $('.imageContainer').length };
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

    if (shown >= number_of_documents) {
      button.hide();
    }else {
      button.css("display", "block");
    }
  }

  function tail(item) { loadNextItems(); }

  function init() {
    endpoint = $(".preview-listing").data("fetch-url");
    number_of_documents = $('.preview-listing').data('number-of-documents');

    var items = document.querySelectorAll(".showroom-item");

    var config = {
      'total': number_of_documents,
      'tail': tail
    };

    if (items.length) {
      showroom = Showroom(items, config);
    }

    toggleShowMoreButton();
    scanForBrokenImages(".preview-listing");
  }

  $(document)
    .on("reload", init)
    .on("viewReady", init)
    .on("click", ".bumblebeeGalleryShowMore", function() {loadNextItems(); });
  $(init);

})(window, window.showroom, window.jQuery);

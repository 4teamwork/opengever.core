(function(global, Showroom, $) {

  var endpoint;
  var showroom;
  var number_of_documents;

  function loadNextItems() {
    var data = { document_pointer: $('.imageContainer').length };
    $.get(endpoint, data).done(function(data) {

      var items = $(data).filter('.imageContainer');
      items.insertAfter($('.imageContainer').last());
      toggleShowMoreButton();
      showroom.append(items);
    });
  }

  function toggleShowMoreButton() {
    var button = $('.showMore');
    var shown = $('.imageContainer').length;

    if (shown >= number_of_documents) {
      button.hide();
    }else {
      button.show();
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
  }

  $(document)
    .on("reload", init)
    .on("click", ".showMore", function() {loadNextItems(); });

  $(init);

})(window, window.showroom, window.jQuery);

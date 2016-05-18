(function(global, Showroom, $) {

  function init() {
    var items = document.querySelectorAll(".showroom-item");

    if (items.length) {
      Showroom(items);
    }
  }

  $(document).on("reload", init);
  $(init);

})(window, window.showroom, window.jQuery);

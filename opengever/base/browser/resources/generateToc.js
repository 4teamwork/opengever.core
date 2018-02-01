(function(global, $, Controller) {

  function downloadFile(url) {

    var loaded = $.Deferred();

    var request = new XMLHttpRequest();

    request.responseType = "blob";
    request.open('GET', url);
    request.send();
    request.onreadystatechange = function() {
      this.onload = function() {
        var contentDisposition = this.getResponseHeader('content-disposition');
        var filename = contentDisposition.match(/filename="(.+)"/)[1];
        var file = URL.createObjectURL(this.response);
        var a = document.createElement("a");
        a.href = file;
        a.download = filename;
        a.click();
      };
      this.onloadend = function() { loaded.resolve(); };
    };

    return loaded;
  }

  function TOCController() {

    Controller.call(this);

    this.downloadTOC = function(target) {
      target.addClass("loading");
      var url = target.attr('href');
      downloadFile(url).done(function() {
        target.removeClass('loading');
      });
    };

    this.events = [
      {
        method: "click",
        target: ".download_toc",
        callback: this.downloadTOC,
      },
    ];

    this.init();

  }

  new TOCController();

})(window, window.jQuery, window.Controller);

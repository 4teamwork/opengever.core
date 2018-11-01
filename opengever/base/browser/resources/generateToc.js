(function(global, $, Controller) {

  function downloadFile(url) {
    var loaded = $.Deferred();
    var request = new XMLHttpRequest();

    request.open('GET', url);
    // ! setting the responseType has to be after the `request.open`
    // `arraybuffer` is necessary for Internet Explorer and Edge becuase
    // they do not support `blob` as response type
    request.responseType = "arraybuffer";
    request.onload = function() {
      loaded.resolve();
      if (this.getResponseHeader('X-ogg-reload-page')) {
        window.location.reload();
      }
      var contentDisposition = this.getResponseHeader('content-disposition');
      var contentType = this.getResponseHeader('content-type');
      var filename = contentDisposition.match(/filename="(.+)"/)[1];
      var file = new Blob([this.response], { type: contentType });
      // For Internet Explorer and Edge
      if ('msSaveOrOpenBlob' in window.navigator) {
        window.navigator.msSaveOrOpenBlob(file, filename);
      }
      // For Firefox and Chrome
      else {
        // Bind blob on disk to ObjectURL
        var data = URL.createObjectURL(file);
        var a = document.createElement("a");
        a.style = "display: none";
        a.href = data;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        // For Firefox
        setTimeout(function(){
          document.body.removeChild(a);
          // Release resource on disk after triggering the download
          window.URL.revokeObjectURL(data);
        }, 100);
      }
    };
    request.onloadend = function() { loaded.resolve(); };
    request.send();

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

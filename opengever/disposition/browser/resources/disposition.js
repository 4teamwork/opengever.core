(function(global, $) {

  function DispositionController() {
    Controller.call(this);

    this.update_appraisal = function(target) {
      return $.post(target.data('url')).done(function(){
        target.toggleClass("active");
        target.siblings().toggleClass("active");
      });
    };

    this.events = [
      {
        method: "click",
        target: ".appraisal-button-group a",
        callback: this.update_appraisal
      }
    ];

    this.init();
  }

  var dispositioncontroller = new DispositionController();

}(window, jQuery));

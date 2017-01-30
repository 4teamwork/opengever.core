(function(global, $) {

  function DispositionController() {
    Controller.call(this);

    this.update_appraisal = function(target) {
      var data = {'dossier-id': target.data('intid'),
                  'should_be_archived': target.data('archive')};
      var url = $('#disposition_overview').data('appraisal_update_url');
      return $.post(url, data).done(function(){
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

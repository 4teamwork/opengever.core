(function(global, $, Controller) {

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

    this.update_repository_appraisal = function(target) {
      var data = {'should_be_archived': target.data('archive'),
                  'dossier-ids': JSON.stringify(
                    target.parent('.action-cell').data('intids'))};
      var url = $('#disposition_overview').data('appraisal_update_url');
      return $.post(url, data).done(function(){
        var repository = target.parents('.repository-list-item');
        if (target.data('archive')){
          repository.find('.icon_button.archive').addClass('active');
          repository.find('.icon_button.not_archive').removeClass('active');
        }
        else {
          repository.find('.icon_button.archive').removeClass('active');
          repository.find('.icon_button.not_archive').addClass('active');
        }
      });
    };

    this.events = [
      {
        method: "click",
        target: ".appraisal-button-group a",
        callback: this.update_appraisal
      },
      {
        method: "click",
        target: ".repo-appraisal-button-group a",
        callback: this.update_repository_appraisal
      }
    ];

    this.init();
  }

  new DispositionController();

}(window, window.jQuery, window.Controller));

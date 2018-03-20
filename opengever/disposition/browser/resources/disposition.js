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

    this.update_transfer_number = function(target){
      var url = $('#transfer_number_dialog').data('transfer-number-save-url');
      return this.request(url, {
        method: "POST",
        data: {
          transfer_number: $('#transfer_number_field').val()
        }
      }).done(function() {
        $('#transfer-number-value').text($('#transfer_number_field').val());
        $('#transfer_number_dialog').data('overlay').close();
      });
    };

    this.cancel_transfer_number = function(target){
      $('#transfer_number_dialog').data('overlay').close();
    };

    this.show_transfer_number_dialog = function(){
      var dialog = $('#transfer_number_dialog')
      if (dialog.data('overlay') === undefined){
        dialog.overlay();
      }
      dialog.data('overlay').load();
    }

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
      },
      {
        method: "click",
        target: ".edit_transfer_number",
        callback: this.show_transfer_number_dialog
      },

      {
        method: "click",
        target: ".save_transfer_number",
        callback: this.update_transfer_number
      },
      {
        method: "click",
        target: ".cancel_transfer_number",
        callback: this.cancel_transfer_number
      }

    ];

    this.init();

  }

  new DispositionController();

}(window, window.jQuery, window.Controller));

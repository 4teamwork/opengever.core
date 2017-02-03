(function(Handlebars, $, MessageFactory) {

  'use strict';

  $(function() {

    var DossierNote = (function () {

      var editNoteLink;
      var overlay;
      var overlayElement;

      function init(){
        editNoteLink = $('#editNoteLink');
        if (!editNoteLink.length) {
          return;
        }

        // Move for correct stacking with overlaymask
        overlayElement = $('#editNoteOverlay');
        $('body').append(overlayElement);
        overlay = overlayElement.overlay().data('overlay');

        // Bind overlay events
        overlay.getOverlay().on('click', 'button.confirm', function(event){
          event.preventDefault();
          saveNote();
        });
        overlay.getOverlay().on('click', 'button.decline', function(event){
          event.preventDefault();
          closeNote();
        });

        overlay.getOverlay().on('onBeforeClose', function(event){
          // Show message if there are unsaved changes
          if (editNoteLink.data('notecache') !== overlay.getOverlay().find('textarea').val()){
            if (confirm('You have unsaved changes, do you really wanna quit')){
              overlay.getOverlay().find('textarea').val(editNoteLink.data('notecache'));
              return true;
            } else {
              return false;
            }
          }
        });
      }

      function successMessage() {
        MessageFactory.getInstance().shout([{
          messageClass: 'info',
          messageTitle: i18n.message_title_info,
          message: i18n.message_body_info
        }]);
      }

      function errorMessage() {
        MessageFactory.getInstance().shout([{
          messageClass: 'error',
          messageTitle: i18n.message_title_error,
          message: i18n.message_body_error
        }]);
      }

      function showNote(){
        overlay.load();
      }

      function closeNote() {
        overlay.close();
      }

      function saveNote() {
        makeRequest({comments: overlay.getOverlay().find('textarea').val()}).done(function(data){
          editNoteLink.data('notecache', overlay.getOverlay().find('textarea').val());
          if (editNoteLink.data('notecache').length) {
            editNoteLink.find('.labelEdit').removeClass('hide');
            editNoteLink.find('.labelAdd').addClass('hide');
          } else {
            editNoteLink.find('.labelEdit').addClass('hide');
            editNoteLink.find('.labelAdd').removeClass('hide');            
          }
          closeNote();
          successMessage();
        }).fail(errorMessage);
      }

      function makeRequest(data, successor){
        var options = {
          url: '.',
          dataType: 'json',
          data: JSON.stringify(data),
          type: 'PATCH',
          headers: {"Accept": "application/json",
                    "Content-Type": "application/json"}
        };
        return $.ajax(options);
      }

      // Bind Edit note link
      $(document).on('click', '#editNoteLink', function(){
        event.preventDefault();
        showNote();
      });

      return {
        init: init,
      };

    })();

    DossierNote.init();
  });
})(window.Handlebars, window.jQuery, window.MessageFactory);

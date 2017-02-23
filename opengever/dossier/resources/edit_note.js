(function(Handlebars, $, MessageFactory) {

  'use strict';

  $(function() {

    var DossierNote = (function () {

      var editNoteLink;
      var overlay;
      var overlayElement;
      var i18n;

      function init(){
        editNoteLink = $('#editNoteLink');
        if (!editNoteLink.length) {
          return;
        }

        i18n = editNoteLink.data('i18n');

        // Move for correct stacking with overlaymask
        overlayElement = $('#editNoteOverlay');
        $('body').append(overlayElement);
        var options = {
          left: 'invalid', // Only way to have no "left" online style on overlay.
          onBeforeLoad: function(event){
            // Set height
            var textarea = overlayElement.find('textarea');
            textarea.height(($(window).height() - textarea.offset().top) * 0.7);
          }
        };
        overlay = overlayElement.overlay(options).data('overlay');

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

          /*
          FIX: If you modify the textarea field for comments in the dossier
          edit form, the newline encoding will be CR+LF (\r\n). After rendering the
          template, the newline-encoding in the textarea will be LF (\n) and in the
          data-attribute it is still CR+LF. Comparing these two strings will always
          return false.

          To fix this issue, we replace the CR+LF newlines with the LF newlines.
           */
          var notecache = editNoteLink.data('notecache').replace(/\r\n/g, '\n');
          if (notecache !== overlay.getOverlay().find('textarea').val()){
            if (confirm(i18n.note_text_confirm_abord)){
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
            editNoteLink.find('.edit').removeClass('hide');
            editNoteLink.find('.add').addClass('hide');
          } else {
            editNoteLink.find('.edit').addClass('hide');
            editNoteLink.find('.add').removeClass('hide');
          }
          closeNote();
          successMessage();
        }).fail(errorMessage);
      }

      function makeRequest(data, successor){
        var options = {
          url: './save_comments',
          data: {data: JSON.stringify(data)},
          type: 'POST',
        };
        return $.ajax(options);
      }

      // Bind Edit note link
      $(document).on('click', '#editNoteLink', function(event){
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

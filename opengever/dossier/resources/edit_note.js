(function(Handlebars, $, MessageFactory) {

  'use strict';

  $(function() {

    var DossierNote = (function () {

      var editNoteLink;
      var notesWrapper;
      var overlay;
      var overlayAPI;
      var overlayElement;
      var i18n;

      function init() {
        editNoteLink = $('#commentsBox > .moreLink');
        notesWrapper = $('.editNoteWrapper');
        if (!editNoteLink.length) {
          return;
        }

        i18n = notesWrapper.data('i18n');

        // Move for correct stacking with overlaymask
        overlayElement = $('#editNoteOverlay');
        $('body').append(overlayElement);
        var options = {
          left: 'invalid', // Only way to have no "left" online style on overlay.
          speed: 0,
          closeSpeed: 0,
          mask: { loadSpeed: 0 }
        };

        var maybeOverlay = overlayElement.overlay(options);
        overlayAPI = maybeOverlay.data && maybeOverlay.data('overlay') ? maybeOverlay.data('overlay') : maybeOverlay;
        overlay = overlayAPI.getOverlay();

        // Bind overlay events
        overlay.one('click', 'button.confirm', function(event){
          event.preventDefault();
          saveNote();
        });
        overlay.on('click', 'button.decline', function(event){
          event.preventDefault();
          closeNote();
        });

        overlay.on('onBeforeClose', function(event){
          // Show message if there are unsaved changes

          /*
          FIX: If you modify the textarea field for comments in the dossier
          edit form, the newline encoding will be CR+LF (\r\n). After rendering the
          template, the newline-encoding in the textarea will be LF (\n) and in the
          data-attribute it is still CR+LF. Comparing these two strings will always
          return false.

          To fix this issue, we replace the CR+LF newlines with the LF newlines.
           */
          var notecache = notesWrapper.data('notecache').replace(/\r\n/g, '\n');
          if (notecache !== overlay.find('textarea').val()){
            if (confirm(i18n.note_text_confirm_abord)){
              overlay.find('textarea').val(notesWrapper.data('notecache'));
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
        overlayAPI.load();
      }

      function closeNote() {
        overlayAPI.close();
      }

      function saveNote() {
        makeRequest({comments: overlay.find('textarea').val()}).done(function(data){
          notesWrapper.data('notecache', overlay.find('textarea').val());
          closeNote();
          successMessage();
          tabbedview.reload_view()
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
      $(document).on('click', '#commentsBox > .moreLink', function(event){
        event.preventDefault();
        showNote();
      });

      return {
        init: init,
      };

    })();

    $(document).on("reload", DossierNote.init);
  });
})(window.Handlebars, window.jQuery, window.MessageFactory);

(function(Handlebars, $, MessageFactory) {

  'use strict';

  $(function() {

    var DossierNote = (function () {

      var noteBox;
      var editNoteLink;
      var editNoteWrapper;
      var overlay;
      var overlayElement;
      var i18n;

      function init(){
        noteBox = $('#commentsBox');
        editNoteLink = $('.editNoteLink');
        if (!editNoteLink.length) {
          return;
        }

        editNoteWrapper = $('.editNoteWrapper');
        i18n = editNoteWrapper.data('i18n');
        // Move for correct stacking with overlaymask
        overlayElement = $('#editNoteOverlay');
        $('body').append(overlayElement);
        var options = {
          left: 'invalid', // Only way to have no "left" online style on overlay.
          onLoad: function(event) {
            event.currentTarget.getOverlay().find('textarea').focus();
          },
          onBeforeLoad: function(event){
            // Set height
            var textarea = overlayElement.find('textarea');
            textarea.height(($(window).height() - textarea.offset().top) * 0.7);
          }
        };

        manipulateDom();

        if (!overlay) {
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
          overlay.getOverlay().on('click', 'button.close', function(event){
            event.preventDefault();
            closeNote();
          });

          overlay.getOverlay().on('click', 'button.delete', function(event){
            event.preventDefault();
            overlayElement.find('textarea').val('');
            saveNote();
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
            var notecache = editNoteWrapper.data('notecache').replace(/\r\n/g, '\n');
            if (notecache !== overlay.getOverlay().find('textarea').val()){
              if (confirm(i18n.note_text_confirm_abord)){
                overlay.getOverlay().find('textarea').val(editNoteWrapper.data('notecache'));
                return true;
              } else {
                return false;
              }
            }
          });

        }
      }

      function manipulateDom() {
        // Move add/edit link to commentBox on overview tab
        if (noteBox.find('.editNoteLink').length === 0) {
          // insert after text if we have a span
          var elem = noteBox.find('span');
          if (elem.length === 0) {
            // insert after header if there is no text yet
            elem = noteBox.find('h2');
          }
          editNoteLink.eq(0).clone().insertAfter(elem);
        }

        // Move add/edit link to title
        if (!overlay) {
          editNoteLink.eq(0).clone().appendTo('h1.documentFirstHeading');
        }

        editNoteLink = $('.editNoteLink');
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
          var comment_container;
          editNoteWrapper.data('notecache', overlay.getOverlay().find('textarea').val());
          if (editNoteWrapper.data('notecache').length) {
            editNoteLink.find('.edit').removeClass('hide');
            editNoteLink.find('.add').addClass('hide');
          } else {
            editNoteLink.find('.edit').addClass('hide');
            editNoteLink.find('.add').removeClass('hide');
          }
          closeNote();
          successMessage();

          comment_container = $('#commentsBox > span');
          if (comment_container.length === 0) {
            comment_container = $('<span></span>').insertAfter($('#commentsBox > h2'));
          }
          comment_container.html(data.comment);
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
      $(document).on('click', '.editNoteLink', function(event){
        event.preventDefault();
        showNote();
      });

      return {
        init: init,
      };

    })();

    $(document).on('reload', '.tabbedview_view', DossierNote.init);
  });
})(window.Handlebars, window.jQuery, window.MessageFactory);

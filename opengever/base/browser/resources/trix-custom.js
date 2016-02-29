(function ($) {

    'use strict';

    /*
    Remove pre, blockquote and links from trix document model to prevent that they can
    be inserted with copy-paste.
     */
    delete Trix.config.blockAttributes.code;
    delete Trix.config.blockAttributes.quote;
    delete Trix.config.textAttributes.href;

    /*
    Prevent accepting file-uploads and attachments in trix.
     */
    $(function () {
        var trixEditor = $('trix-editor');
        trixEditor.on('trix-file-accept', function (event) {
            event.preventDefault();
        });
        trixEditor.on("trix-attachment-add", function (event) {
            event.originalEvent.attachment.remove();
        });
    });

}(jQuery));

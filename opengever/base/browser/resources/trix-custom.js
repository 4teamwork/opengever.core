(function ($, Trix) {

    'use strict';

    /*
    Remove pre, blockquote and links from trix document model to prevent that they can
    be inserted with copy-paste.
     */
    delete Trix.config.blockAttributes.code;
    delete Trix.config.blockAttributes.quote;
    delete Trix.config.blockAttributes.heading1;
    delete Trix.config.textAttributes.href;
    delete Trix.config.textAttributes.frozen;
    delete Trix.config.textAttributes.strike;

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

}(jQuery, window.Trix));

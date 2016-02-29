/*
Remove links from trix document model to prevent that links can be copy-pasted
into trix even though we have disabled the link buttons.
 */
delete Trix.config.textAttributes.href

/*
Prevent accepting file-uploads in trix.
 */
$(function() {
    $('trix-editor').on('trix-file-accept', function(event) {
        event.preventDefault();
    });
});

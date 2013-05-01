// GEVER specifig formsubmithelper, wich disallow a second submit

function inputSubmitOnClick(event) {
    if (jQuery(this).hasClass('submitting') && !jQuery(this).hasClass('allowMultiSubmit'))
        return false;
    else
        jQuery(this).addClass('submitting');
}

(function($) { $(function() {
    $('input:submit').each(function() {
      if (!this.onclick)
        $(this).click(inputSubmitOnClick);
    });
}); })(jQuery);

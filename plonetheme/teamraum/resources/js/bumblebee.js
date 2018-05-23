$(document).on('click', '.colorboxLinkSearchView', function(){
  ftwFileBumblebeeOverlay.$last_opened_preview = $(this);
  return ftwFileBumblebeeOverlay.openPreview(
      ftwFileBumblebeeOverlay.$last_opened_preview)
});

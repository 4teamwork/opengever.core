function setTourAsSeen(tourKey) {
  var url = $( 'body' ).data('base-url') + '/@user-settings';
  var requester = axios.create();
  requester.defaults.headers.common['Accept'] = 'application/json';
  requester.defaults.headers.common['Content-Type'] = 'application/json';

  requester.get(url).then(function(data) {
    var seenTours = data.data.seen_tours;
    if(!(tourKey in seenTours)) {
      requester.patch(url, { 'seen_tours': seenTours.concat([tourKey]) });
    }
  });
}

$(document).ready(function(){
  $('#close-frontend-teaser').on('click', addTour);

  function addTour() {
    var element = $(this);
    setTourAsSeen(element.data('tourkey'));
    element.closest('.teaser').hide();
  }
});

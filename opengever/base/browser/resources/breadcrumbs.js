(function($) {

  function getDropdown(toggler) {
    return $(toggler).parent().next('.repo-dropdown').get(0);
  }

  function toggleDropdown(element) {
    getDropdown(element).classList.toggle('dropdown-open');
  }

  function closeDropdown(element) {
    getDropdown(element).classList.remove('dropdown-open');
  }

  function isSameElement(target, context) {
    return target !== context && !context.contains(target);
  }

  function trackDropdown(dropdownToggle) {
    dropdownToggle.addEventListener('click', function(event) {
      event.preventDefault();
      toggleDropdown(dropdownToggle);
    });

    window.addEventListener('click', function(event) {
      if (isSameElement(event.target, dropdownToggle)) {
        closeDropdown(dropdownToggle);
      }
    });
  }

  $(function() {
    [].slice.call(document.querySelectorAll('.repo-dropdown-toggle')).forEach(trackDropdown);
  });

})(window.jQuery);

(function() {
  sitesToBeDeleted.forEach(function(site) {
    try {
      document.querySelector('a[href="' + site + '"]').parentNode.style.display = 'none';
    } catch (e) {}
  });

  var selectors = [
    '#header-main-tab-bar .dropdown',
    '#header-top-bar-left',
    '#header-top-bar-right',
    '#header-top-bar-left > .dropdown',
    '#header-top-bar-right > .dropdown',
  ];

  function closeMenu(e) {
    if (e.target.classList.value.indexOf('opened') !== -1) {
      e.stopPropagation();
    }
    var elem = document.querySelector('.opened');
    elem.classList.remove('opened');
    document.removeEventListener('click', closeMenu, true);
  }

  selectors.forEach(function(selector) {
    var elem = document.querySelector(selector);
    elem.addEventListener(
      'click',
      function(elem) {
        this.classList.add('opened');
        document.removeEventListener('click', closeMenu, true);
        document.addEventListener('click', closeMenu, true);
      },
      false
    );
  });
})();

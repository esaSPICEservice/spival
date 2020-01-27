window.onload = function() {
  var fileExplorer = document.querySelector('.file-explorer');
  if (fileExplorer) {
    fileExplorer.style.height =
      fileExplorer.contentWindow.document.body.offsetHeight + 20 + 'px';
  }

  // hide sidebar when it ahs no contents
  var sideBar = document.querySelector('#ht-sidebar');
  if (sideBar && sideBar.innerText === '') {
    sideBar.remove();
  }
};

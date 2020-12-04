function setActiveLinkInNavbar() {
  /*
    Sets the href for the current
    page's link in the navbar to
    '#' instead of the page address
  */
  $activeLink = $('.active').find('a');
  $activeLink.attr('href', '#')
}

$(() => {
  setActiveLinkInNavbar()
});
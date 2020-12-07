// I want to remove form from add_league
// page once the add league btn is clicked

function setActiveLinkInNavbar() {
  /*
    Sets the href for the current
    page's link in the navbar to
    '#' instead of the page address
  */
  $activeLink = $('.active').find('a');
  $activeLink.attr('href', '#');
}

function setAddLeagueBtnLink() {
  /*
   Sets the add league button
   to redirect to /add-league 
   */
  $btn = $('#add-league-btn')
  $btn.click(() => {
    location.pathname = '/add-league'
  });
}

$(() => {
  setActiveLinkInNavbar();
  setAddLeagueBtnLink();
});
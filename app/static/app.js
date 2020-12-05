function setActiveLinkInNavbar() {
  /*
    Sets the href for the current
    page's link in the navbar to
    '#' instead of the page address
  */
  $activeLink = $('.active').find('a');
  $activeLink.attr('href', '#');
}

function addLeagueBtn() {
  try {
    $btn = $('#add-league-btn')
    $btn.click((event) => {
      location.pathname = '/add-league'
    });
  }
  catch (err) {
    console.log('Not on right page!')
  }
}

$(() => {
  setActiveLinkInNavbar();
  addLeagueBtn();
});
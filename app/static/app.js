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

function addDeleteAccountAlert() {
  /*
  Adds an alert to user profile
  to confirm if the user would like to
  delete their account
  */
  $btn = $('#delete-btn')
  $btn.click((event) => {
    event.preventDefault();
    isProceeding = confirm('Are you sure you would like to delete your account?')
    if (isProceeding) {
      $user_id = $('#user-id').text();
      location = `/users/${$user_id}/delete`
    }
  });
}

$(() => {
  setActiveLinkInNavbar();
  setAddLeagueBtnLink();
  addDeleteAccountAlert();
});
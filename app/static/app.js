// I want to remove form from add_league
// page once the add league btn is clicked

function setActiveLinkInNavbar() {
  /*
    Sets the href for the current
    page's link in the navbar to
    '#' instead of the page address
  */
  const $activeLink = $('.active').find('a');
  $activeLink.attr('href', '#');
}

function setAddLeagueBtnLink() {
  /*
   Sets the add league button
   to redirect to /add-league 
   */
  const $btn = $('#add-league-btn')
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
    let isProceeding = confirm('Are you sure you would like to delete your account?')
    if (isProceeding) {
      let $user_id = $('#user-id').text();
      location = `/users/${$user_id}/delete`
    }
  });
}

function addLoadingScreen() {
  const $content = $('.container-fluid')
  const $addLeagueForm = $('#add-league-form')
  $addLeagueForm.submit(() => {
    const $loadingRow = $('<div class="row">')
    const $loadingCol = $('<div class="col-12 text-center">')
    const $loadingDiv = $('<i class="fas fa-spinner fa-pulse fa-3x">')
    $loadingCol.append($loadingDiv)
    $loadingRow.append($loadingCol)
    $content.append($loadingRow)
  });
}

async function addPlayerButtons() {
  const $hiddenDiv = $('#player_stats_div')
  const $statsBtn = $('#player_stats_btn')
  $statsBtn.click(async () => {
    if ($hiddenDiv.parent().is(':visible')) {
      $hiddenDiv.empty();
      $hiddenDiv.parent().hide();
      return;
    }
    else {
      let $playerId = $('#js-player-id').data('player-id');
      let response = await axios.get(`/players/${$playerId}/stats-data`);
      let stats = response.data.stats;
      for (let stat of stats) {
        let $statDiv = $('<div class="d-flex justify-content-between">');
        let statName = stat['name'];
        let statVal = stat['value'];
        let $statText = $('<p class="lead">');
        $statText.text(`${statName}`);
        let $statSpanText = $('<p class="lead">');
        $statSpanText.text(`${statVal}`);
        $statDiv.append($statText).append($statSpanText);
        $hiddenDiv.append($statDiv);
      }
      $hiddenDiv.parent().show();
    }
  });
}

$(async () => {
  setActiveLinkInNavbar();
  setAddLeagueBtnLink();
  addDeleteAccountAlert();
  addLoadingScreen();
  await addPlayerButtons();
});
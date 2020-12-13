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

function addDeleteLeagueAlert() {
  /*
  Adds an alert so users dont accidentally delete their
  league by accident
  */
  $btn = $('#delete-league-btn')
  $btn.click((event) => {
    event.preventDefault();
    let isProceeding = confirm('Are you sure you would like to delete this league?')
    if (isProceeding) {
      let $leagueId = $('#js-league-id').data('league-id');
      location = `/leagues/${$leagueId}/delete`
    }
  });
}

function addNewLeagueLoadingScreen() {
  /*
  Adds loading icon to add league
  page after add league button is
  pressed
  */
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

async function addStatsListener($hiddenDiv, $statsBtn) {
  /*
  Adds the event listener to the stats
  button on the player page
  */
  $statsBtn.click(async () => {
    if ($hiddenDiv.parent().is(':visible')) {
      $hiddenDiv.empty();
      $hiddenDiv.parent().hide();
      // Hide all titles
      $('#outlook-title-name').hide();
      $('#outlook-title-val').hide();
      $('#stat-title-name').hide()
      $('#stat-title-val').hide()
      return;
    }
    else {
      $('#stat-title-name').show()
      $('#stat-title-val').show()
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

async function addOutlooksListener($hiddenDiv, $outlooksBtn) {
  /*
  Adds the event listener to the outlooks
  button on the player page
  */
  $outlooksBtn.click(async () => {
    if ($hiddenDiv.parent().is(':visible')) {
      $hiddenDiv.empty();
      $hiddenDiv.parent().hide();
      // Hide all titles
      $('#outlook-title-name').hide();
      $('#outlook-title-val').hide();
      $('#stat-title-name').hide()
      $('#stat-title-val').hide()
      return;
    }
    else {
      $('#outlook-title-name').show();
      $('#outlook-title-val').show();
      let $playerId = $('#js-player-id').data('player-id');
      let response = await axios.get(`/players/${$playerId}/outlooks-data`);
      let outlooks = response.data.outlooks;
      for (let outlook of outlooks) {
        let $outlookDiv = $('<div class="d-flex justify-content-between border-bottom">');
        let week = outlook['week'];
        let look = outlook['outlook'];
        let $weekText = $('<p class="h6">');
        $weekText.text(`Week ${week}: `);
        let $outlookText = $('<p class="lead ml-5">');
        $outlookText.text(`${look}`);
        $outlookDiv.append($weekText).append($outlookText);
        $hiddenDiv.append($outlookDiv);
      }
      $hiddenDiv.parent().show();
    }
  });
}

async function addPlayerListeners() {
  /*
  Adds event listeners to the stats and
  outlooks buttons on the player page
  */
  const $hiddenDiv = $('#player_stats_div');
  const $statsBtn = $('#player_stats_btn');
  const $outlooksBtn = $('#player_outlooks_btn');
  await addStatsListener($hiddenDiv, $statsBtn);
  await addOutlooksListener($hiddenDiv, $outlooksBtn);
}

function getPlayerIds(tradeStr) {
  /*
  Get the player IDs from the trade
  suggestion to pass to /users/userId/save-trade
  */
  let trades = [];
  parsedTrades = tradeStr.split('>, ');
  for (let trade of parsedTrades) {
    trade = trade.replace('<', '');
    trade = trade.replace('>', '');
    trade = trade.replace('[', '');
    trade = trade.replace(']', '');
    trade = trade.replace('PlayerModel ', '');
    new_arr = trade.split(' team_id')
    id = new_arr[0].split('=')[1];
    id = parseInt(id);
    trades.push(id);
  }
  return trades;
}

async function saveTrade(tradeStr, userId, tradingPlayerId) {
  /*
  Gets an array of player ids from
  getPlayerIds, and sends them in a post
  request to /users/<userId>/save-trade
  Then alerts 'Trade Saved!' to the user
  */
  let trades = getPlayerIds(tradeStr);
  let response = await axios.post(`/users/${userId}/save-trade`, { trading_player_id: tradingPlayerId, player_ids: trades });
  alert('Trade Saved!');
}

async function addSaveTradeListener() {
  /*
  Adds event listener to save trade button
  so users can save their trades to profile
  */
  const $tradeBtn = $('#save-trade-btn');
  $tradeBtn.click(async () => {
    let tradeStr = $('#js-player-trades').data('trades');
    let userId = $('#js-user-id').data('user-id');
    let tradingPlayerId = $('#js-player-id').data('player-id');
    await saveTrade(tradeStr, userId, tradingPlayerId);
  });
}

async function addPageItems() {
  /*
  Adds necessary items to the page,
  as well as event listeners on 
  necessary page elements
  */
  setActiveLinkInNavbar();
  setAddLeagueBtnLink();
  addDeleteAccountAlert();
  addDeleteLeagueAlert();
  addNewLeagueLoadingScreen();
  await addPlayerListeners();
  await addSaveTradeListener();
}

$(async () => {
  await addPageItems();
});
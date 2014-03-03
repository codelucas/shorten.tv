// Code for shorten.tv. Most of the youtube related code, like
// autoplaying videos and autcomplete was taken from Feross's 
// project: youtubeinstant.com, check it out!
// http://youtubeinstant.com

google.load("swfobject", "2.1");
google.load("jquery", "1.4.2");

var INITIAL_VID_THUMBS = 5;

function _run() {
  loadPlayer();
}

function loadPlayer() {
  currentVideoId = "TTpfMLV6STQ";
  var params = {
    allowScriptAccess: "always"
  };
  var atts = {
    id: "ytPlayer",
    allowFullScreen: "true"
  };
  swfobject.embedSWF("http://www.youtube.com/v/" + currentVideoId + "&enablejsapi=1&playerapiid=ytplayer" + "&rel=0&autoplay=0&egm=0&loop=0&fs=1&hd=0&showsearch=0&showinfo=0&iv_load_policy=3&cc_load_policy=1", "innerVideoDiv", "720", "405", "8", null, null, params, atts);
}

function onYouTubePlayerReady(playerId) {
  ytplayer = document.getElementById("ytPlayer");
  ytplayer.addEventListener("onStateChange", "onPlayerStateChange");
  var searchBox = $("#searchBox");
  searchBox.keyup(doInstantSearch);
  $(document.documentElement).keydown(onKeyDown);
  $("#buttonControl").click(playPause);
  $("#linkUrl").click(function(e) {
    $(this).select();
  });
  if (window.location.hash) {
    var searchTerm = $('<div/>').text(getHash()).html(); // escape html
    $("#searchBox").val(searchTerm).focus();
  } else {
    var defaultSearches = [ "Rihanna", "Usher", "Katy Perry", "Eminem", "Shakira", "Taylor Swift", "Akon", "Lady Gaga", "Paramore", "Jay Z", "Led Zepplin", "Guns N Roses", "Aerosmith", "Borat", "Fallout Boy", "Blink 182", "Justin Bieber", "Drake"];
    var randomNumber = Math.floor(Math.random() * defaultSearches.length);
    $("#searchBox").val(defaultSearches[randomNumber]).select().focus();
  }
  onBodyLoad();
  doInstantSearch();
}

function onBodyLoad() {
  currentSearch = "";
  currentSuggestion = "";
  currentVideoId = "";
  playlistShowing = false;
  playlistArr = [];
  currentPlaylistPos = 0;
  currentPlaylistPage = 0;
  xhrWorking = false;
  pendingSearch = false;
  pendingDoneWorking = false;
  playerState = -1;
  hashTimeout = false;
  mainSequence = null;
  flaskXhr = null;
  // loadRandomTip();
}

function onPlayerStateChange(newState) {
  playerState = newState;
  if (pendingDoneWorking && playerState == 1) {
    doneWorking();
    pendingDoneWorking = false;
  } else if (playerState === 0) {
    // doneWorking();
    goNextVideo();
  }
}

function onKeyDown(e) {
  if (e.keyCode == 39 || e.keyCode == 40) {
    //goNextVideo();
  } else if (e.keyCode == 37 || e.keyCode == 38) {
    //goPrevVideo();
  } else if (e.keyCode == 13) {
    //playPause();
  }
}

function goNextVideo() {
  if (currentPlaylistPos == INITIAL_VID_THUMBS - 1) {
    return;
  }
  goVid(currentPlaylistPos + 1, currentPlaylistPage);
}

function goPrevVideo() {
  if (currentPlaylistPos === 0) {
    return;
  }
  goVid(currentPlaylistPos - 1, currentPlaylistPage);
}

function getCurTitle() {
  return playlistArr[currentPlaylistPage][currentPlaylistPos].title;
}

function goVid(playlistPos, playlistPage) {
  if (playlistPage != currentPlaylistPage) {
    currentPlaylistPage = playlistPage;
    return;
  }
  loadAndPlayVideo(playlistArr[playlistPage][playlistPos].id, playlistPos);
}

function doInstantSearch() {
  if (flaskXhr) {
    flaskXhr.abort();
    xhrWorking = false;
  }
  if (xhrWorking) {
    pendingSearch = true;
    return;
  }
  var searchBox = $("#searchBox");
  if (searchBox.val() == currentSearch) {
    return;
  }

  currentSearch = searchBox.val();
  if (searchBox.val() === "") {
    $("#playlistWrapper").slideUp("slow");
    playlistShowing = false;
    pauseVideo();
    clearVideo();
    updateHash("");
    currentSuggestion = "";
    updateSuggestedKeyword("Search YouTube Instantly");
    return;
  }

  searchBox.attr("class", "statusLoading");
  keyword = searchBox.val();
  var the_url = "http://suggestqueries.google.com/complete/search?hl=en&ds=yt&client=youtube&hjson=t&jsonp=window.yt.www.suggest.handleResponse&q=" + encodeURIComponent(searchBox.val()) + "&cp=1";
  $.ajax({
    type: "GET",
    url: the_url,
    dataType: "script"
  });
  xhrWorking = true;
}

yt = {};

yt.www = {};

yt.www.suggest = {};

yt.www.suggest.handleResponse = function(suggestions) {
  if (suggestions[1][0]) {
    var searchTerm = suggestions[1][0][0];
  } else {
    var searchTerm = null;
  }
  updateHash(currentSearch);
  if (!searchTerm) {
    searchTerm = keyword;
    updateSuggestedKeyword(searchTerm + " (Exact search)");
  } else {
    updateSuggestedKeyword(searchTerm);
    if (searchTerm == currentSuggestion) {
      doneWorking();
      return;
    }
  }
  getTopSearchResult(searchTerm);
  currentSuggestion = searchTerm;
};

function getTopSearchResult(keyword) {
  var the_url = "http://gdata.youtube.com/feeds/api/videos?q=" + encodeURIComponent(keyword) + "&format=5&max-results=" + INITIAL_VID_THUMBS + "&v=2&alt=jsonc";
  $.ajax({
    type: "GET",
    url: the_url,
    dataType: "jsonp",
    success: function(responseData, textStatus, XMLHttpRequest) {
      if (responseData.data.items) {
        var videos = responseData.data.items;
        playlistArr = [];
        playlistArr.push(videos);
        updateVideoDisplay(videos);
        pendingDoneWorking = true;
      } else {
        updateSuggestedKeyword('No results for "' + keyword + '"');
        doneWorking();
      }
    }
  });
}

function updateVideoDisplay(videos) {
  var numThumbs = videos.length >= INITIAL_VID_THUMBS ? INITIAL_VID_THUMBS : videos.length;
  var playlist = $("<div />").attr("id", "playlist");
  for (var i = 0; i < numThumbs; i++) {
    var videoId = videos[i].id;
    var img = $("<img />").attr("src", videos[i].thumbnail.sqDefault);
    var a = $("<a />").attr("href", "javascript:loadAndPlayVideo('" + videoId + "', " + i + ")");
    var title = $("<div />").html(videos[i].title);
    playlist.append(a.append(img).append(title));
  }
  var playlistWrapper = $("#playlistWrapper");
  $("#playlist").remove();
  playlistWrapper.append(playlist);
  if (!playlistShowing) {
    playlistWrapper.slideDown("slow");
    playlistShowing = true;
  }
  currentPlaylistPos = -1;
  if (currentVideoId != videos[0].id) {
    loadAndPlayVideo(videos[0].id, 0, true);
  }
}

function doneWorking() {
  xhrWorking = false;
  if (pendingSearch) {
    pendingSearch = false;
    doInstantSearch();
  }
  var searchBox = $("#searchBox");
  searchBox.attr("class", "statusPlaying");
}

function updateHTML(elmId, value) {
  document.getElementById(elmId).innerHTML = value;
}

function updateSuggestedKeyword(keyword) {
  updateHTML("searchTermKeyword", keyword);
}

function updateHash(hash) {
  var timeDelay = 1e3;
  if (hashTimeout) {
    clearTimeout(hashTimeout);
  }
  hashTimeout = setTimeout(function() {
    window.location.replace("#" + encodeURI(hash));
    $("#linkUrl").val(window.location);
    document.title = '"' + currentSuggestion.toTitleCase() + '" on shorten.tv!';
  }, timeDelay);
  
}

function getHash() {
  return decodeURIComponent(window.location.hash.substring(1));
}

function loadRandomTip() {
  var tips = [ 
      "Don't touch the video player! It will disrupt the summarization.", 
      "Don't press the video player! Everything takes care of itself.", 
      "Every time you type a letter, a new video loads!" 
  ];
  var randomNumber = Math.floor(Math.random() * tips.length);
  $("#tip").html("<u>Quick tip</u>: " + tips[randomNumber]);
}

function loadVideo(videoId) {
  if (ytplayer) {
    ytplayer.cueVideoById(videoId);
    currentVideoId = videoId;
  }
}

function playVideo() {
  if (ytplayer) {
    ytplayer.playVideo();
  }
}

function seekTo(startTime) {
  if (ytplayer) {
    ytplayer.seekTo(startTime);
  }
}

function clearCurSequence() {
  $('#videoTitle').html(
    '<span class="blackLight"> Generating video summary ...</span></div>');
  $('#videoMetaData').html('');

  if (flaskXhr) {
    flaskXhr.abort();
    xhrWorking = false;
  }
  clearTimeout(mainSequence);
  clearHighlights();
}

function highlightTime(index) {
  clearHighlights();
  $('span.timeclip'+index.toString()).css('color', '#df691a');
  $('span.timeclip'+index.toString()).css('font-weight', '700');
  $('span.timeclip'+index.toString()).css('font-size', '19px');
}

function clearHighlights() {
  // clear all old bolds
  $('span.timeclip').css('font-weight', '300');
  $('span.timeclip').css('color', '#fff');
  $('span.timeclip').css('font-size', '15px');
}

function playHotClips(videoId) {
  if (ytplayer) {
    // ytplayer.cueVideoById(videoId);
    ytplayer.loadVideoById(videoId);
    var i = 0;                  
    var hotClips = [];
    var startTime = 0;
    var endTime = 0;
    var delta = 0;

    flaskXhr = $.post('/shorten/', { yt_id: videoId },
      function(response) {
        if (!response) {
          return;
        }
        var strHotClips = response.hotclips;
        var prettyHotClips = response.pretty_hotclips;

        hotClips = jQuery.parseJSON(strHotClips);
        prettyHotClips = jQuery.parseJSON(prettyHotClips);
        var hotclipString = "";

        for (var j=0; j<prettyHotClips.length; j++) {
          hotclipString = hotclipString + " <span class='timeclip timeclip" + 
            j.toString() + "'>(" + 
            prettyHotClips[j][0] + ", " + prettyHotClips[j][1] + ")</span>";           
        }

        // 'Duration: <i>' + response.duration + '</i><br>
        $('#videoMetaData').html('Summarized Clips: <i>' + hotclipString+'</i>');

        var title = getCurTitle();
        $('#videoTitle').html('<strong>'+title+'</strong>');

        replay();
      }, 'json'
    );

    function sequence() {        
      mainSequence = setTimeout(function() { 
        if (i == hotClips.length) {
          i = 0;  // failed
          goNextVideo();
          return;
        }
        highlightTime(i);
        var curTup = hotClips[i];
        startTime = curTup[0];
        endTime = curTup[1];
        delta = (endTime - startTime) * 1000;
        delta += 3000;  // youtube api lag time

        // alert('we are currently seeking to ' + startTime + ' clips: '+ hotClips);
        seekTo(startTime);
        playVideo();
        i++;                
        if (i == hotClips.length) { 
          setTimeout(function() {
            i = 0;
            goNextVideo();
          }, delta);
        } else if (i < hotClips.length) {      
          sequence();      
        }
       }, delta);
    }

    function replay() {
      i = 0;
      sequence();
    }
  }
}

function loadAndPlayVideo(videoId, playlistPos, bypassXhrWorkingCheck) {
  if (currentPlaylistPos == playlistPos) {
    playPause();
    return;
  }
  if (!bypassXhrWorkingCheck && xhrWorking) {
    return;
  }

  clearCurSequence();

  if (ytplayer) {
    xhrWorking = true;
    playHotClips(videoId);
    currentVideoId = videoId;
    pendingDoneWorking = true;
  }

  currentPlaylistPos = playlistPos;
  $("#playlistWrapper").removeClass("play0 play1 play2 play3 play4 pauseButton playButton").addClass("pauseButton play" + playlistPos);
  var playlist = $("#playlist");
  playlist.children().removeClass("selectedThumb");
  playlist.children(":nth-child(" + (playlistPos + 1) + ")").addClass("selectedThumb");
}

function setPlaybackQuality(quality) {
  if (ytplayer) {
    ytplayer.setPlaybackQuality(quality);
  }
}

function pauseVideo() {
  if (ytplayer) {
    ytplayer.pauseVideo();
  }
}

function clearVideo() {
  if (ytplayer) {
    ytplayer.clearVideo();
  }
}

function getVideoUrl() {
  alert(ytplayer.getVideoUrl());
}

function playPause() {
  if (ytplayer) {
    if (playerState == 1) {
      pauseVideo();
      $("#playlistWrapper").removeClass("pauseButton").addClass("playButton");
    } else if (playerState == 2) {
      playVideo();
      $("#playlistWrapper").removeClass("playButton").addClass("pauseButton");
    }
  }
}

String.prototype.toTitleCase = function() {
  return this.replace(/([\w&`'‘’"“.@:\/\{\(\[<>_]+-? *)/g, function(match, p1, index, title) {
    if (index > 0 && title.charAt(index - 2) !== ":" && match.search(/^(a(nd?|s|t)?|b(ut|y)|en|for|i[fn]|o[fnr]|t(he|o)|vs?\.?|via)[ \-]/i) > -1) return match.toLowerCase();
    if (title.substring(index - 1, index + 1).search(/['"_{(\[]/) > -1) return match.charAt(0) + match.charAt(1).toUpperCase() + match.substr(2);
    if (match.substr(1).search(/[A-Z]+|&|[\w]+[._][\w]+/) > -1 || title.substring(index - 1, index + 1).search(/[\])}]/) > -1) return match;
    return match.charAt(0).toUpperCase() + match.substr(1);
  });
};

google.setOnLoadCallback(_run);

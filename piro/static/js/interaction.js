
//SUGGESTED CHALLENGES PAGE
$('.challengepanel').on('click', function() {

	$(location).attr('href', 'selectexistingchallenge.html');

});


//FRIENDS/UPDATES PAGE

$('#friendstab').on('click', function() {

	$('#friendstab').css({'background': '#068D9D', 'color': 'white'});
	$('#friendspanel').css({'z-index': '100000'});
	$('#updatestab').css({'background': 'white', 'color': '#068D9D'});
	$('#updatespanel').css({'z-index': '99999'});

});

$('#updatestab').on('click', function() {

	$('#updatestab').css({'background': '#068D9D', 'color': 'white'});
	$('#updatestab').css({'z-index': '100000'});
	$('#friendstab').css({'background': 'white', 'color': '#068D9D'});
	$('#friendspanel').css({'z-index': '99999'});

});


$('.woot').on('click', function() {

	$('#wootalert').css({'visibility': 'visible'});
	$('#wootalert').animate({'height': '70px', 'width':'160px', 'left': '80px', 'top': '70px'}, 300);

	setTimeout(function() {

		$('#wootalert').css({'visibility': 'hidden'});
		$('#wootalert').css({'height': '0px', 'width':'0px', 'left': '160px', 'top': '140px'})}, 1300);


});


//CREATE NEW CHALLENGE PAGE

$('#visibilityprivate').on('click', function() {

	$('#visibilityprivate').css({'background': '#068D9D', 'color': 'white'});
	$('#visibilitypublic').css({'background': 'white', 'color': '#068D9D'});

});

$('#visibilitypublic').on('click', function() {

	$('#visibilitypublic').css({'background': '#068D9D', 'color': 'white'});
	$('#visibilityprivate').css({'background': 'white', 'color': '#068D9D'});

});

$('#accept').on('click', function() {

    $(location).attr('href', 'dashboard.html');

});

//DASHBOARD PAGE
$('.activechallenge').on('click', function() {

	$(location).attr('href', 'challengecomplete.html');

});

$('#navbutton1').on('click', function() {

    $(location).attr('href', 'dashboard.html');

});

$('#navbutton2').on('click', function() {

    $(location).attr('href', 'analytics.html');

});

$('#navbutton3').on('click', function() {

    $(location).attr('href', 'friendsupdates.html');

});

$('#navbutton4').on('click', function() {

    $(location).attr('href', 'suggestedchallenges.html');

});
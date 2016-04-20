// Ionic Starter App

// angular.module is a global place for creating, registering and retrieving Angular modules
// 'starter' is the name of this angular module example (also set in a <body> attribute in index.html)
// the 2nd parameter is an array of 'requires'
var ionicApp = angular.module('todo', ['ionic', 'ngCordova']);


ionicApp.run(function($ionicPlatform) {
  $ionicPlatform.ready(function() {
    if(window.cordova && window.cordova.plugins.Keyboard) {
      // Hide the accessory bar by default (remove this to show the accessory bar above the keyboard
      // for form inputs)
      cordova.plugins.Keyboard.hideKeyboardAccessoryBar(true);

      // Don't remove this line unless you know what you are doing. It stops the viewport
      // from snapping when text inputs are focused. Ionic handles this internally for
      // a much nicer keyboard experience.
      cordova.plugins.Keyboard.disableScroll(true);
    }
    if(window.StatusBar) {
      StatusBar.styleDefault();
    }


    function show_notification(){

      var now = new Date().getTime(),
      _5_sec_from_now = new Date(now + 5*1000);
      cordova.plugins.notification.local.schedule({
          id: 10,
          at: _5_sec_from_now,
          title: "We have a new memory for you!",
          text: "Take a look inside",
      });

      // cordova.plugins.notification.local.on("schedule", function(notification) {
      //   alert("scheduled: " + notification.id);
      // });

      // cordova.plugins.notification.local.on("trigger", function(notification) {
      //   alert("triggered: " + notification.id);
      // });
    }

    // This function returns the storj hashes of 5 random compact discs
    function get_random_hashes() {
     var baseUrl = 'http://localhost:5000/api/v1';
     var endpoint = '/getRandomDisk';
     var constructedUrl = baseUrl + endpoint;


      $.get(constructedUrl, {

        'key': 'b26ec1c3585573cf4914d8f16b7cc895'
        // 'key': false
      }, function success(response) {
        console.log(response);
      });
    }

    document.addEventListener("deviceready", onDeviceReady, false);
    function onDeviceReady() {

      var uri = encodeURI("https://s-media-cache-ak0.pinimg.com/236x/c5/3f/4e/c53f4e6cc8875b2e8ef13cd415ce7ad3.jpg");
      var filename = uri.split("/").pop();
      var filePath = cordova.file.dataDirectory + filename;

      // Displays a locally stored image on the UI
      function displayAsset(filePath){
        $("#image").attr('src', filePath );
      }

      // checks if the file exists, If yes displays directly else downloads and displays it
      function download_and_display_picture(){
        window.resolveLocalFileSystemURL(filePath,
                                        function(){ displayAsset(filePath)},
                                        function(){ local_storage.downloadFromRemote(uri, filePath)});
      }

      $("#show_picture").on('click', download_and_display_picture);
    }

    $("#noti_link").on('click', show_notification);
    $("#get-random-hashes").on('click', get_random_hashes);
  });
});

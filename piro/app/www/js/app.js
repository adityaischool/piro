// Ionic Starter App

// angular.module is a global place for creating, registering and retrieving Angular modules
// 'starter' is the name of this angular module example (also set in a <body> attribute in index.html)
// the 2nd parameter is an array of 'requires'
angular.module('todo', ['ionic'])


.run(function($ionicPlatform) {
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

    function show_notification(title, text){

      var now             = new Date().getTime(),
      _5_sec_from_now = new Date(now + 5*1000);
      cordova.plugins.notification.local.schedule({
          id: 10,
          at: _5_sec_from_now,
          title: "Meeting in 15 minutes!",
          text: "Jour fixe Produktionsbesprechung",
      });

      cordova.plugins.notification.local.on("schedule", function(notification) {
        alert("scheduled: " + notification.id);
      });

      cordova.plugins.notification.local.on("trigger", function(notification) {
        alert("triggered: " + notification.id);
      });
    }

    $("#noti_link").click(show_notification("Title", "Text"));
  })
})

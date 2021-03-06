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

    var memoryDisks = [];

    var sampleDisks = [
    '{\"snoozeDate\": 0, \"themeSongs\": [{\"spotifyImgUrl\": \"https://i.scdn.co/image/d62e58c1f4ae8607b4af7fa8a377e437c49e3abc\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c296c36cd08d9f333e0b38e80d582085384edc90\", \"artist\": \"Black Marble\", \"track\": \"A Different Arrangement\", \"dataPointId\": \"lastfm1364743583.0\", \"playCount\": 2}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/d62e58c1f4ae8607b4af7fa8a377e437c49e3abc\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c296c36cd08d9f333e0b38e80d582085384edc90\", \"artist\": \"Black Marble\", \"track\": \"A Different Arrangement\", \"dataPointId\": \"lastfm1364743583.0\", \"playCount\": 2}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/d62e58c1f4ae8607b4af7fa8a377e437c49e3abc\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c296c36cd08d9f333e0b38e80d582085384edc90\", \"artist\": \"Black Marble\", \"track\": \"A Different Arrangement\", \"dataPointId\": \"lastfm1364743583.0\", \"playCount\": 2}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/d62e58c1f4ae8607b4af7fa8a377e437c49e3abc\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c296c36cd08d9f333e0b38e80d582085384edc90\", \"artist\": \"Black Marble\", \"track\": \"A Different Arrangement\", \"dataPointId\": \"lastfm1364743583.0\", \"playCount\": 2}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/d62e58c1f4ae8607b4af7fa8a377e437c49e3abc\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c296c36cd08d9f333e0b38e80d582085384edc90\", \"artist\": \"Black Marble\", \"track\": \"A Different Arrangement\", \"dataPointId\": \"lastfm1364743583.0\", \"playCount\": 2}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/d62e58c1f4ae8607b4af7fa8a377e437c49e3abc\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c296c36cd08d9f333e0b38e80d582085384edc90\", \"artist\": \"Black Marble\", \"track\": \"A Different Arrangement\", \"dataPointId\": \"lastfm1364743583.0\", \"playCount\": 2}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/d62e58c1f4ae8607b4af7fa8a377e437c49e3abc\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c296c36cd08d9f333e0b38e80d582085384edc90\", \"artist\": \"Black Marble\", \"track\": \"A Different Arrangement\", \"dataPointId\": \"lastfm1364743583.0\", \"playCount\": 2}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/d62e58c1f4ae8607b4af7fa8a377e437c49e3abc\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c296c36cd08d9f333e0b38e80d582085384edc90\", \"artist\": \"Black Marble\", \"track\": \"A Different Arrangement\", \"dataPointId\": \"lastfm1364743583.0\", \"playCount\": 2}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/d62e58c1f4ae8607b4af7fa8a377e437c49e3abc\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c296c36cd08d9f333e0b38e80d582085384edc90\", \"artist\": \"Black Marble\", \"track\": \"A Different Arrangement\", \"dataPointId\": \"lastfm1364743583.0\", \"playCount\": 2}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/d62e58c1f4ae8607b4af7fa8a377e437c49e3abc\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c296c36cd08d9f333e0b38e80d582085384edc90\", \"artist\": \"Black Marble\", \"track\": \"A Different Arrangement\", \"dataPointId\": \"lastfm1364743583.0\", \"playCount\": 2}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/d62e58c1f4ae8607b4af7fa8a377e437c49e3abc\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c296c36cd08d9f333e0b38e80d582085384edc90\", \"artist\": \"Black Marble\", \"track\": \"A Different Arrangement\", \"dataPointId\": \"lastfm1364743583.0\", \"playCount\": 2}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/d62e58c1f4ae8607b4af7fa8a377e437c49e3abc\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c296c36cd08d9f333e0b38e80d582085384edc90\", \"artist\": \"Black Marble\", \"track\": \"A Different Arrangement\", \"dataPointId\": \"lastfm1364743583.0\", \"playCount\": 2}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/673648e6441897f0c64de454ccbaed0e42248711\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/4070a844e31fc9179e2d17214c818a8d11390ac2\", \"artist\": \"Teen Daze\", \"track\": \"Brooklyn Sunburn\", \"dataPointId\": \"lastfm1364739359.0\", \"playCount\": 2}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/d62e58c1f4ae8607b4af7fa8a377e437c49e3abc\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c296c36cd08d9f333e0b38e80d582085384edc90\", \"artist\": \"Black Marble\", \"track\": \"A Different Arrangement\", \"dataPointId\": \"lastfm1364743583.0\", \"playCount\": 2}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/673648e6441897f0c64de454ccbaed0e42248711\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/4070a844e31fc9179e2d17214c818a8d11390ac2\", \"artist\": \"Teen Daze\", \"track\": \"Brooklyn Sunburn\", \"dataPointId\": \"lastfm1364739359.0\", \"playCount\": 2}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/d62e58c1f4ae8607b4af7fa8a377e437c49e3abc\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c296c36cd08d9f333e0b38e80d582085384edc90\", \"artist\": \"Black Marble\", \"track\": \"A Different Arrangement\", \"dataPointId\": \"lastfm1364743583.0\", \"playCount\": 2}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/673648e6441897f0c64de454ccbaed0e42248711\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/4070a844e31fc9179e2d17214c818a8d11390ac2\", \"artist\": \"Teen Daze\", \"track\": \"Brooklyn Sunburn\", \"dataPointId\": \"lastfm1364739359.0\", \"playCount\": 2}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/d62e58c1f4ae8607b4af7fa8a377e437c49e3abc\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c296c36cd08d9f333e0b38e80d582085384edc90\", \"artist\": \"Black Marble\", \"track\": \"A Different Arrangement\", \"dataPointId\": \"lastfm1364743583.0\", \"playCount\": 2}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/673648e6441897f0c64de454ccbaed0e42248711\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/4070a844e31fc9179e2d17214c818a8d11390ac2\", \"artist\": \"Teen Daze\", \"track\": \"Brooklyn Sunburn\", \"dataPointId\": \"lastfm1364739359.0\", \"playCount\": 2}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/d62e58c1f4ae8607b4af7fa8a377e437c49e3abc\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c296c36cd08d9f333e0b38e80d582085384edc90\", \"artist\": \"Black Marble\", \"track\": \"A Different Arrangement\", \"dataPointId\": \"lastfm1364743583.0\", \"playCount\": 2}], \"name\": \"Sun Mar 31, 2013\", \"people\": [], \"dataPointIds\": [\"dropbox1364709002.0\", \"dropbox1364709015.0\", \"dropbox1364709402.0\", \"dropbox1364722334.0\", \"dropbox1364722795.0\", \"dropbox1364722820.0\", \"dropbox1364723322.0\", \"dropbox1364723692.0\", \"dropbox1364723862.0\", \"dropbox1364724212.0\", \"dropbox1364724223.0\", \"dropbox1364727217.0\", \"dropbox1364727650.0\", \"dropbox1364727681.0\", \"dropbox1364728113.0\", \"dropbox1364728733.0\", \"dropbox1364731667.0\", \"dropbox1364732015.0\", \"dropbox1364732016.0\", \"dropbox1364732016.0\", \"dropbox1364732016.0\", \"instagram1364775626.0\", \"instagram1364775840.0\", \"instagram1364775958.0\", \"instagram1364776238.0\", \"instagram1364776412.0\", \"instagram1364776496.0\", \"instagram1364776624.0\"], \"notes\": [], \"userId\": \"b26ec1c3585573cf4914d8f16b7cc895\", \"locations\": [], \"emotions\": [], \"displayStatus\": \"on\", \"weather\": [], \"date\": \"20130331\", \"_id\": {\"$oid\": \"57149ae4534b4449980bdde0\"}, \"creationTimestamp\": 1460942963.551, \"diskUserEngagement\": {\"diskLastModified\": 0, \"diskLastViewed\": 0, \"diskModified\": false, \"diskTotalViews\": 0, \"diskTimesModified\": 0, \"diskLastPlayed\": 0, \"diskTotalPlays\": 0, \"diskTotalSkips\": 0}, \"diskId\": \"20130331001\"}',
    '{\"snoozeDate\": 0, \"themeSongs\": [], \"name\": \"Udaipur City, 24\", \"people\": [], \"dataPointIds\": [\"dropbox1452075224.0\", \"dropbox1452077564.0\", \"dropbox1452077573.0\", \"dropbox1452077612.0\", \"dropbox1452110624.0\", \"dropbox1452110656.0\", \"dropbox1452110716.0\", \"dropbox1452110733.0\", \"dropbox1452110760.0\", \"dropbox1452119734.0\", \"dropbox1452120293.0\", \"dropbox1452120312.0\", \"dropbox1452121328.0\", \"dropbox1452121751.0\", \"dropbox1452122315.0\", \"dropbox1452122318.0\", \"dropbox1452122323.0\", \"dropbox1452122325.0\", \"dropbox1452133519.0\", \"dropbox1452133550.0\", \"dropbox1452133763.0\"], \"notes\": [], \"userId\": \"b26ec1c3585573cf4914d8f16b7cc895\", \"locations\": [{\"placeName\": \"Vile, 16\", \"coords\": {\"lat\": 19.096666666666664, \"long\": 72.85444444444444}, \"businessName\": null}, {\"placeName\": \"Mander, 09\", \"coords\": {\"lat\": 24.62, \"long\": 73.88944444444445}, \"businessName\": null}, {\"placeName\": \"Udaipur City, 24\", \"coords\": {\"lat\": 24.585555555555555, \"long\": 73.69638888888889}, \"businessName\": null}, {\"placeName\": \"Udaipur, Rajasthan\", \"coords\": {\"lat\": 24.579444444444444, \"long\": 73.68027777777779}, \"businessName\": {\"city\": \"Udaipur\", \"region\": \"Rajasthan\", \"name\": \"Hotel Thamla Haveli\"}}], \"emotions\": [], \"displayStatus\": \"on\", \"weather\": [{\"weather\": {\"moonPhaseValue\": 0.87, \"maxTemp\": 88.43, \"precipType\": \"rain\", \"minTemp\": 73, \"cloudCover\": 0, \"humidity\": 0.45, \"pressure\": 1014.34, \"windSpeed\": 1.29, \"precipProbability\": null, \"sunset\": 1452084353, \"visibility\": 1.49, \"moonPhaseName\": \"waning-crescent\", \"summary\": \"Foggy throughout the day.\", \"sunrise\": 1452044665, \"icon\": \"fog\"}, \"location\": {\"placeName\": \"Vile, 16\", \"coords\": {\"lat\": 19.096666666666664, \"long\": 72.85444444444444}, \"businessName\": null}}, {\"weather\": {\"moonPhaseValue\": 0.87, \"maxTemp\": 82.33, \"precipType\": \"rain\", \"minTemp\": 50, \"cloudCover\": 0.09, \"humidity\": 0.59, \"pressure\": 1017.06, \"windSpeed\": 2.53, \"precipProbability\": null, \"sunset\": 1452083466, \"visibility\": 2.86, \"moonPhaseName\": \"waning-crescent\", \"summary\": \"Partly cloudy starting in the evening.\", \"sunrise\": 1452045056, \"icon\": \"partly-cloudy-night\"}, \"location\": {\"placeName\": \"Mander, 09\", \"coords\": {\"lat\": 24.62, \"long\": 73.88944444444445}, \"businessName\": null}}, {\"weather\": {\"moonPhaseValue\": 0.87, \"maxTemp\": 82.33, \"precipType\": \"rain\", \"minTemp\": 50, \"cloudCover\": 0.09, \"humidity\": 0.59, \"pressure\": 1017.06, \"windSpeed\": 2.53, \"precipProbability\": null, \"sunset\": 1452083516, \"visibility\": 2.86, \"moonPhaseName\": \"waning-crescent\", \"summary\": \"Partly cloudy starting in the evening.\", \"sunrise\": 1452045098, \"icon\": \"partly-cloudy-night\"}, \"location\": {\"placeName\": \"Udaipur City, 24\", \"coords\": {\"lat\": 24.585555555555555, \"long\": 73.69638888888889}, \"businessName\": null}}, {\"weather\": {\"moonPhaseValue\": 0.87, \"maxTemp\": 87.15, \"precipType\": \"rain\", \"minTemp\": 50.86, \"cloudCover\": 0.01, \"humidity\": 0.58, \"pressure\": 1016.11, \"windSpeed\": 1, \"precipProbability\": null, \"sunset\": 1452083521, \"visibility\": 2.85, \"moonPhaseName\": \"waning-crescent\", \"summary\": \"Clear throughout the day.\", \"sunrise\": 1452045101, \"icon\": \"clear-day\"}, \"location\": {\"placeName\": \"Udaipur, Rajasthan\", \"coords\": {\"lat\": 24.579444444444444, \"long\": 73.68027777777779}, \"businessName\": {\"city\": \"Udaipur\", \"region\": \"Rajasthan\", \"name\": \"Hotel Thamla Haveli\"}}}], \"date\": \"20160106\", \"_id\": {\"$oid\": \"57149ab2534b444754f458df\"}, \"creationTimestamp\": 1460942913.751, \"diskUserEngagement\": {\"diskLastModified\": 0, \"diskLastViewed\": 0, \"diskModified\": false, \"diskTotalViews\": 0, \"diskTimesModified\": 0, \"diskLastPlayed\": 0, \"diskTotalPlays\": 0, \"diskTotalSkips\": 0}, \"diskId\": \"20160106001\"}',
    '{\"snoozeDate\": 0, \"themeSongs\": [{\"spotifyImgUrl\": \"https://i.scdn.co/image/2b296372202df7e045bdaea3358fb581ba28f401\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/bd1c022cc2d6a407157bd4a453ce2969548bce31\", \"artist\": \"Amtrac\", \"track\": \"Came Along - Amtrac\\u2019s Summer Mix\", \"dataPointId\": \"lastfm1454603790.0\", \"playCount\": 1}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/2b296372202df7e045bdaea3358fb581ba28f401\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/bd1c022cc2d6a407157bd4a453ce2969548bce31\", \"artist\": \"Amtrac\", \"track\": \"Came Along - Amtrac\\u2019s Summer Mix\", \"dataPointId\": \"lastfm1454603790.0\", \"playCount\": 1}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/0402ab998323d93aef19a3b8855bf2193721d7dd\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/ec8bbffa02bd45b445b4ad537868019ddd14a10e\", \"artist\": \"Amtrac\", \"track\": \"Hold On - Original Mix\", \"dataPointId\": \"lastfm1454594648.0\", \"playCount\": 1}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/acf62034fb87b16bf727ead60b0412f78bac17c2\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c04cfc467f9623cfe309e85397f2f6eaa012da87\", \"artist\": \"Olympic Ayres\", \"track\": \"Control\", \"dataPointId\": \"lastfm1454610266.0\", \"playCount\": 1}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/2b296372202df7e045bdaea3358fb581ba28f401\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/bd1c022cc2d6a407157bd4a453ce2969548bce31\", \"artist\": \"Amtrac\", \"track\": \"Came Along - Amtrac\\u2019s Summer Mix\", \"dataPointId\": \"lastfm1454603790.0\", \"playCount\": 1}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/0402ab998323d93aef19a3b8855bf2193721d7dd\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/ec8bbffa02bd45b445b4ad537868019ddd14a10e\", \"artist\": \"Amtrac\", \"track\": \"Hold On - Original Mix\", \"dataPointId\": \"lastfm1454594648.0\", \"playCount\": 1}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/acf62034fb87b16bf727ead60b0412f78bac17c2\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c04cfc467f9623cfe309e85397f2f6eaa012da87\", \"artist\": \"Olympic Ayres\", \"track\": \"Control\", \"dataPointId\": \"lastfm1454610266.0\", \"playCount\": 1}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/2b296372202df7e045bdaea3358fb581ba28f401\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/bd1c022cc2d6a407157bd4a453ce2969548bce31\", \"artist\": \"Amtrac\", \"track\": \"Came Along - Amtrac\\u2019s Summer Mix\", \"dataPointId\": \"lastfm1454603790.0\", \"playCount\": 1}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/0402ab998323d93aef19a3b8855bf2193721d7dd\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/ec8bbffa02bd45b445b4ad537868019ddd14a10e\", \"artist\": \"Amtrac\", \"track\": \"Hold On - Original Mix\", \"dataPointId\": \"lastfm1454594648.0\", \"playCount\": 1}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/250f26c5e403963d4cca03ddc5c061543af9a868\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c08864726ff308973f6228978073035c3dcc6540\", \"artist\": \"Amtrac\", \"track\": \"Once is Enough\", \"dataPointId\": \"lastfm1454593895.0\", \"playCount\": 1}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/acf62034fb87b16bf727ead60b0412f78bac17c2\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c04cfc467f9623cfe309e85397f2f6eaa012da87\", \"artist\": \"Olympic Ayres\", \"track\": \"Control\", \"dataPointId\": \"lastfm1454610266.0\", \"playCount\": 1}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/2b296372202df7e045bdaea3358fb581ba28f401\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/bd1c022cc2d6a407157bd4a453ce2969548bce31\", \"artist\": \"Amtrac\", \"track\": \"Came Along - Amtrac\\u2019s Summer Mix\", \"dataPointId\": \"lastfm1454603790.0\", \"playCount\": 1}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/e82da086bd6db6b8648dcccdd858c1c2c363eefd\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/0aa897478a36f35d43d055addb3e07c13505236b\", \"artist\": \"Amtrac\", \"track\": \"Without Warning - Amtrac Remix\", \"dataPointId\": \"lastfm1454603098.0\", \"playCount\": 1}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/0402ab998323d93aef19a3b8855bf2193721d7dd\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/ec8bbffa02bd45b445b4ad537868019ddd14a10e\", \"artist\": \"Amtrac\", \"track\": \"Hold On - Original Mix\", \"dataPointId\": \"lastfm1454594648.0\", \"playCount\": 1}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/250f26c5e403963d4cca03ddc5c061543af9a868\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c08864726ff308973f6228978073035c3dcc6540\", \"artist\": \"Amtrac\", \"track\": \"Once is Enough\", \"dataPointId\": \"lastfm1454593895.0\", \"playCount\": 1}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/501097e151080a472cbbfed3e316de3ae329e0aa\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/922550079cb834df14433c956654244e6eb7f886\", \"artist\": \"The Juan Maclean\", \"track\": \"Running Back to You\", \"dataPointId\": \"lastfm1454611231.0\", \"playCount\": 1}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/acf62034fb87b16bf727ead60b0412f78bac17c2\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/c04cfc467f9623cfe309e85397f2f6eaa012da87\", \"artist\": \"Olympic Ayres\", \"track\": \"Control\", \"dataPointId\": \"lastfm1454610266.0\", \"playCount\": 1}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/2b296372202df7e045bdaea3358fb581ba28f401\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/bd1c022cc2d6a407157bd4a453ce2969548bce31\", \"artist\": \"Amtrac\", \"track\": \"Came Along - Amtrac\\u2019s Summer Mix\", \"dataPointId\": \"lastfm1454603790.0\", \"playCount\": 1}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/e82da086bd6db6b8648dcccdd858c1c2c363eefd\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/0aa897478a36f35d43d055addb3e07c13505236b\", \"artist\": \"Amtrac\", \"track\": \"Without Warning - Amtrac Remix\", \"dataPointId\": \"lastfm1454603098.0\", \"playCount\": 1}, {\"spotifyImgUrl\": \"https://i.scdn.co/image/0402ab998323d93aef19a3b8855bf2193721d7dd\", \"spotifyPreviewUrl\": \"https://p.scdn.co/mp3-preview/ec8bbffa02bd45b445b4ad537868019ddd14a10e\", \"artist\": \"Amtrac\", \"track\": \"Hold On - Original Mix\", \"dataPointId\": \"lastfm1454594648.0\", \"playCount\": 1}], \"name\": \"San Francisco, CA\", \"people\": [], \"dataPointIds\": [\"dropbox1454575653.0\", \"dropbox1454575758.0\", \"dropbox1454575761.0\", \"dropbox1454576307.0\", \"dropbox1454576316.0\", \"dropbox1454576338.0\", \"dropbox1454576341.0\", \"dropbox1454576343.0\", \"dropbox1454576535.0\", \"dropbox1454576823.0\", \"dropbox1454576829.0\", \"dropbox1454576832.0\", \"dropbox1454577128.0\", \"dropbox1454577142.0\", \"dropbox1454577169.0\", \"dropbox1454577613.0\", \"dropbox1454577618.0\", \"dropbox1454577624.0\", \"dropbox1454577626.0\", \"dropbox1454577772.0\", \"dropbox1454577775.0\", \"dropbox1454577777.0\", \"dropbox1454577913.0\", \"dropbox1454577917.0\", \"dropbox1454577934.0\", \"dropbox1454577948.0\", \"dropbox1454578439.0\", \"dropbox1454578441.0\", \"dropbox1454578443.0\", \"dropbox1454578447.0\", \"dropbox1454578501.0\", \"dropbox1454579056.0\", \"dropbox1454579059.0\", \"dropbox1454579064.0\", \"dropbox1454579084.0\", \"dropbox1454579211.0\", \"dropbox1454579337.0\", \"dropbox1454579353.0\", \"dropbox1454579380.0\", \"dropbox1454579456.0\", \"dropbox1454579458.0\", \"dropbox1454579462.0\"], \"notes\": [], \"userId\": \"b26ec1c3585573cf4914d8f16b7cc895\", \"locations\": [{\"placeName\": \"San Francisco, CA\", \"coords\": {\"lat\": 37.78361111111111, \"long\": -122.50944444444444}, \"businessName\": null}], \"emotions\": [], \"displayStatus\": \"on\", \"weather\": [{\"weather\": {\"moonPhaseValue\": 0.83, \"maxTemp\": 53, \"precipType\": \"rain\", \"minTemp\": 41.82, \"cloudCover\": null, \"humidity\": null, \"pressure\": 1028.08, \"windSpeed\": 4.58, \"precipProbability\": null, \"sunset\": 1454549774, \"visibility\": null, \"moonPhaseName\": \"waning-crescent\", \"summary\": \"Clear throughout the day.\", \"sunrise\": 1454512438, \"icon\": \"clear-day\"}, \"location\": {\"placeName\": \"San Francisco, CA\", \"coords\": {\"lat\": 37.78361111111111, \"long\": -122.50944444444444}, \"businessName\": null}}], \"date\": \"20160204\", \"_id\": {\"$oid\": \"57149a5b534b443adccafc8e\"}, \"creationTimestamp\": 1460942825.683, \"diskUserEngagement\": {\"diskLastModified\": 0, \"diskLastViewed\": 0, \"diskModified\": false, \"diskTotalViews\": 0, \"diskTimesModified\": 0, \"diskLastPlayed\": 0, \"diskTotalPlays\": 0, \"diskTotalSkips\": 0}, \"diskId\": \"20160204001\"}'
    ];


    for (index in sampleDisks) {
      var parsedSampleDisk = processMemoryDiskTextFileOutput(sampleDisks[index]);
      memoryDisks.push(parsedSampleDisk);
    }

    console.log('memory disks', memoryDisks);


    function processMemoryDiskTextFileOutput(textFileOutput) {
      var text = textFileOutput;
      text = text.replace(/\\/gi, '');
      console.log('sample disk as string', text);
      var parsedSampleDisk = JSON.parse(text);
      console.log('parsed sample disk', parsedSampleDisk);
      return parsedSampleDisk;
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

    //Local File Storage Sample Code
    var uri = encodeURI("https://s-media-cache-ak0.pinimg.com/236x/c5/3f/4e/c53f4e6cc8875b2e8ef13cd415ce7ad3.jpg");
    var filename = uri.split("/").pop();
    var filePath = cordova.file.dataDirectory + filename;

    // Displays a locally stored image on the UI

    document.addEventListener("deviceready", function(){
      //Download file from a remote server and store it locally (Data Directory)
      function downloadFromRemote(uri, filePath){
        var fileTransfer = new FileTransfer();
        fileTransfer.download(
            uri,
            filePath,
            function(entry) {
                console.log("download complete: " + entry.fullPath);
            },
            function(error) {
                console.log("download error source " + error.source);
                console.log("download error target " + error.target);
                console.log("upload error code" + error.code);
            },
            false,
            {
                headers: {
                    "Authorization": "Basic dGVzdHVzZXJuYW1lOnRlc3RwYXNzd29yZA=="
                }
            }
        );
      }

      function displayAsset(filePath){
        $("#image").attr('src', filePath );
      }

      // checks if the file exists, If yes displays directly else downloads and displays it
      function download_and_display_picture(){
        window.resolveLocalFileSystemURL(filePath,
                                        function(){ displayAsset(filePath)},
                                        function(){ downloadFromRemote(uri, filePath)});
      }

      $("#show_picture").on('click', download_and_display_picture);

    }, false);


    //Storj mimic Sample code
    function storj_fetch_file_given_hash(storj_hash){
      // call storj api for file download
      alert("hello");
      console.log(JSON.parse(sampleDisks[0]));
    }

    // Input: compact disk object
    // Output: Images on the disk
    function fetch_images_on_disk(compact_disk_object){
      var full_stroj_hash = "";//compact_disk_object['storjHash'];
      full_disk_object = storj_fetch_file_given_hash(full_stroj_hash);
      // image_list = list()
    }

    //In progress
    function test_blockchain(){
        storj_fetch_file_given_hash("");
    }

    $("#blockchain").on('click', test_blockchain);
    $("#noti_link").on('click', show_notification);
    $("#get-random-hashes").on('click', get_random_hashes);
  });
});

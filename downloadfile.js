// 570c997da2ae841d2ea9798e
'use strict';

var fs = require('fs');

var bridge = require('storj-bridge-client');

// Authenticate with credentials
var client = new bridge.Client('https://api.storj.io', {
  basicauth: {
    email: 'bigchobbit@gmail.com',
    password: '12345678'
  }
});
//get all hashes, then create pull token for each hash; then filepointer and download
var bucket = '570c997da2ae841d2ea9798e';
var hash="d4e7115c59024334a0cdadedfe70ee23e6dccf61"
client.createToken(bucket, 'PULL').then(function(token) {
  // Fetch the file pointer list
  console.log(token.token)
  return client.getFilePointer(bucket, token.token, hash);
}).then(function(pointers) {
	//console.log(pointers)
	//console.log(client.resolveFileFromPointers(pointers))
  //return "x"
  console.log("download variable pre");
  var download=client.resolveFileFromPointers(pointers)
  console.log("download variable done");
  //console.log(download);
  var destination = fs.createWriteStream('f.txt');
  // Write downloaded file to disk
  download.pipe(destination);
  console.log("done")});



/*client.createToken(bucket, 'PULL').then(function(token) {
  // Fetch the file pointer list
  return client.listFilesInBucket(bucket, token.token, filehash);
}).then(function(pointers) {
  // Open download stream from network and a writable file stream
  var download = client.resolveFileFromPointers(pointers);
  var destination = fs.createWriteStream('<write_file_to_path>');
  // Write downloaded file to disk
  download.pipe(destination);

  lis=client.listFilesInBucket(bucket).then(function(x){console.log(x);console.log(x[0].hash); 
hash=x[0].hash}).then(function(hash){
console.log("enter")
cl=client.getFilePointer(bucket,"",hash).then(function(y){
//console.log(pointers)
var download = client.resolveFileFromPointers(hash);
  var destination = fs.createWriteStream('f.txt');
  // Write downloaded file to disk
  console.log(download.pipe(destination));
console.log("done")});});
console.log(lis);

[ { bucket: '570c997da2ae841d2ea9798e',
    mimetype: 'text/plain',
    filename: 'file.txt',
    size: 7,
    hash: 'd4e7115c59024334a0cdadedfe70ee23e6dccf61' } ]

});*/
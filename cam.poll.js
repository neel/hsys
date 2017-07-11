var NodeWebcam = require("node-webcam");
var http = require("http");

// require('global-tunnel').initialize({
//   tunnel: 'both',
//   host: '192.168.250.21',
//   port: 3128
// });

var opts = {
    quality: 50,
    delay: 0,
    saveShots: true,
    output: "jpeg",
    device: false,
    callbackReturn: "base64",
    verbose: false
};
 
 
//Creates webcam instance 
 
var Webcam = NodeWebcam.create(opts);

function frame(req){
    var webcam = NodeWebcam.create(opts);
    webcam.capture("frame", function(err, data){
        req.end(JSON.stringify({"data": data}));
    });
}

function feed(){
    var opts = {
        host: '192.168.250.21',
        port: 3128,
        path: 'http://remotehealth.org:8000/pulse/talkpoll/0',
        method: 'POST'
    };
    var req = http.request(opts, function(res){
        setTimeout(function(){
            res.setEncoding('utf8');
            res.on('data', function(chunk){
                console.log(chunk);
            });
            feed();
        }, 500);
    });
    frame(req);
}


 
process.env['NODE_TLS_REJECT_UNAUTHORIZED'] = '0';
feed();
// var ON_DEATH = require('death');
// ON_DEATH(function(signal, err){
//     console.log("Disconnecting on Keyboard interrupt");

// })

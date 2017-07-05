var NodeWebcam = require( "node-webcam" );

var opts = {
    quality: 12,
    delay: 0,
    saveShots: true,
    output: "jpeg",
    device: false,
    callbackReturn: "base64",
    verbose: false
};
 
 
//Creates webcam instance 
 
var Webcam = NodeWebcam.create( opts );

var WebSocketClient = require('websocket').client;
var client = new WebSocketClient();
 
client.on('connectFailed', function(error) {
    console.log('Connect Error: ' + error.toString());
});
var gcon;
client.on('connect', function(connection) {
    gcon = connection;
    console.log('WebSocket Client Connected');
    connection.on('error', function(error) {
        console.log("Connection Error: " + error.toString());
    });
    connection.on('close', function() {
        console.log('Connection Closed');
    });
    connection.on('message', function(message) {
        // discard message
        console.log("Received ", message);
        frame(connection);
    });
    
    function frame(conn){
        var webcam = NodeWebcam.create(opts);
        webcam.capture("frame", function(err, data){
            console.log(err);
            console.log(data);
            conn.send(data);
        });
    }
    frame(connection);
});
 
process.env['NODE_TLS_REJECT_UNAUTHORIZED'] = '0';
client.connect('wss://remotehealth.org/pulse/talksock');
var ON_DEATH = require('death');
ON_DEATH(function(signal, err){
    console.log("Disconnecting on Keyboard interrupt");
    gcon.close();
})

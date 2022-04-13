$(document).ready(function() {
    const socket = io();

    socket.on("connect", function() {
        console.log("socket connected");
        socket.emit("message", "I'm connected!");
    });

    socket.on("message", function(message) {
        console.log("received message");
        $("#messages").append("<li>Received message: " + message +  "</li>");
    });
});

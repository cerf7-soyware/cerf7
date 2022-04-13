// noinspection JSUnresolvedFunction

const socket = io();

socket.on("connect", () => {
    console.log("Connected to server WebSocket")
});

// Update dialog list and dialog messages.
// Expected format: message = {opponentId: ..., messageJson: ...} where
// `messageJson` defines message body.
socket.on("chat-message", message => {
    console.log("Received a message from character");
    console.log(message)
});

// Update cache of available user actions.
socket.on("available-conversation", message => {
    console.log("Received available option for chat");
    console.log(message);
});

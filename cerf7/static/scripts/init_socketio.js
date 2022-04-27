// noinspection JSUnresolvedFunction

const socket = io();
let availableActionsCache = new AvailableActionsCache();
let dialogsCache = new DialogsCache();

socket.on("connect", () => {
    console.log("Connected to server WebSocket");
});

// Update dialog list and dialog messages.
// Expected format: message = {opponent_id: ..., message_body: ...}.
socket.on("npc-message", (message) => {
    console.log("NPC message: " + message);
    // onNpcMessage(message);
});

// Update cache of available user actions.
socket.on("available-message", (message) => {
    console.log("Available message: " + message);
    // onAvailableMessage(message);
});

socket.on("main-character-offline", () => {
    console.log("Main character is offline");
});

socket.on("main-character-back-online", () => {
    console.log("Main character is back online");
});

socket.on("message-expiration", (message) => {
    console.log("Message expiration: " + message);
});

// Log all messages for debugging purposes
socket.on("message", (message) => {
    console.log("General purpose message from server: " + message);
});

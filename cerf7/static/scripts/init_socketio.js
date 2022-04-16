// noinspection JSUnresolvedFunction

const socket = io();
let availableActionsCache = new AvailableActionsCache();
let dialogsCache = new DialogsCache();

socket.on("connect", () => {
    console.log("Connected to server WebSocket")
});

// Update dialog list and dialog messages.
// Expected format: message = {opponent_id: ..., message_json: ...} where
// `message_json` defines message body.
socket.on("chat-message", onChatMessage);

// Update cache of available user actions.
socket.on("available-conversation", onAvailableAction);

function onChatMessage(message) {
    // Update cache of dialog list and dialog messages
    if (dialogsCache.dialogs === null) {
        dialogsCache.dialogs = [];
    }
    dialogsCache.dialogs.append(message);
}

function onAvailableAction(action) {
    // Update cache of available actions
    if (availableActionsCache.availableActions === null) {
        availableActionsCache.availableActions = [];
    }
    availableActionsCache.availableActions.append(action);
}

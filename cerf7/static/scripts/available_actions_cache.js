class AvailableActionsCache {
    // Lazy-loaded cache of available user actions
    constructor() {
        this.availableActions = null;
        // if null should be downloaded from server immediately
        // if [] then no options
        // otherwise contains some objects in an array
    }
}

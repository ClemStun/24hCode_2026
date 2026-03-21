import { keybindsManager } from "./keybinds.js";
import api from "./api.js";

class GameEvent extends Event {
    constructor(type, options) {
        super(type, options);
    }
}

class Game {
    get _api() {
        return api;
    }

    constructor() {
        this.keybindsManager = keybindsManager;
    }

    init() {
        document.addEventListener('keydown', (event) => {
            for (const action in this.keybindsManager.keybinds) {
                if (this.keybindsManager.keybinds[action].includes(event.code)) {
                    document.dispatchEvent(new GameEvent(`game.${action}`, { game: this }));
                }
            }
        });
    }

    async onShutdown() {
        await this.keybindsManager.onShutdown();
        await this._api.onShutdown(); // Ensure API shutdown is called after keybindsManager
    }
}

export { Game, GameEvent };
export default Game;
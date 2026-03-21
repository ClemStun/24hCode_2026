import { api } from './api.js';

class KeybindsManager {
    static get ACTIONS() {
        return Object.keys(this.DEFAULT_KEYBINDS);
    }

    static DEFAULT_KEYBINDS = {
        'move_up': ['ArrowUp', 'KeyW', 'KeyZ'],
        'move_down': ['ArrowDown', 'KeyS'],
        'move_left': ['ArrowLeft', 'KeyA', 'KeyQ'],
        'move_right': ['ArrowRight', 'KeyD'],
        'action': ['Space', 'Enter'],
        'menu': ['Escape']
    };

    static _langage = {
        'move_up': 'Déplacer vers le haut',
        'move_down': 'Déplacer vers le bas',
        'move_left': 'Déplacer vers la gauche',
        'move_right': 'Déplacer vers la droite',
        'action': 'Action'
    };
    static get langage() {
        return this._langage;
    }

    _keybinds = {};
    get keybinds() {
        return { ...this._keybinds };
    }
    set keybinds(newKeybinds) {
        this._keybinds = { ...this._keybinds, ...newKeybinds };
        this._saveKeybindsToServer();
    }

    constructor() {
        this.init();
    }

    async init() {
        const savedKeybinds = await this._fetchKeybindsFromServer();
        this._keybinds = { ...savedKeybinds, ...KeybindsManager.DEFAULT_KEYBINDS };
        await this._saveKeybindsToServer();
    }

    changeKeybind(action, newKeys) {
        if (!KeybindsManager.ACTIONS.includes(action)) {
            throw new Error(`Action "${action}" is not a valid action.`);
        }

        this.keybinds = { [action]: newKeys };
    }

    updateKeybinds(newKeybinds) {
        this.keybinds = newKeybinds;
    }

    resetKeybind(action) {
        if (!KeybindsManager.ACTIONS.includes(action)) {
            throw new Error(`Action "${action}" is not a valid action.`);
        }

        this.keybinds = { [action]: KeybindsManager.DEFAULT_KEYBINDS[action] };
    }

    resetKeybinds() {
        this.keybinds = KeybindsManager.DEFAULT_KEYBINDS;
    }

    async _fetchKeybindsFromServer() {
        return await api.get('/api/keybinds/');
    }

    async _saveKeybindsToServer() {
        return await api.post('/api/keybinds/', { data: this._keybinds });
    }

    async onShutdown() {
        await api.onShutdown();
    }
}

const keybindsManager = new KeybindsManager();
export { keybindsManager };
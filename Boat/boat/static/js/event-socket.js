const ws = new WebSocket(`ws://127.0.0.1:8001/ws`);

class EventSocket {
    _callbacks = {};

    constructor() {
        this._socket = ws;
        this._socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            Object.entries(this._callbacks)
                .filter(([key, _]) => key === data.type || key === 'Any')
                .forEach(([_, callback]) => {
                    callback.forEach(cb => cb(data));
                });
        };
    }

    on(eventType, callback) {
        this._callbacks[eventType] ??= [];
        this._callbacks[eventType].push(callback);
    }

    off(eventType, callback) {
        if (!this._callbacks[eventType]) return;
        this._callbacks[eventType] = this._callbacks[eventType].filter(cb => cb !== callback);
    }
}

const eventSocket = new EventSocket();
export default eventSocket;
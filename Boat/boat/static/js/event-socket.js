const ws = new WebSocket(`ws://${window.location.host}/ws`);

class EventSocket {
    _callbacks = {};

    constructor() {
        this._socket = ws;
        this._socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            Object.entries(this._callbacks)
                .filter(([key, _]) => key === data.type)
                .forEach(([_, callback]) => {
                    callback(data);
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
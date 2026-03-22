import { Api } from "./api.js";

class Move {
    _api = new Api('http://localhost:8000/');

    async moveNext(direction) {
        console.log('move next', direction);
        console.log(await this._api.post('/api/move/', {
            data: { direction }
        }));
    }

    async moveTo(x, y) {
        await this._api.post('/api/move/', {
            data: { x, y }
        })
    }
}

const move = new Move();
export { move };
export default move;
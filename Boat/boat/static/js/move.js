import { Api } from "./api.js";

class Move {
    _api = new Api('http://localhost:8000/');

    async moveNext(direction) {
        console.log('move next', direction);

        return await this._api.post('/api/move/', {
            data: { direction },
            successMessage: `Déplacement vers ${direction} réussi !`,
            errorMessage: `Échec du déplacement vers ${direction}.`
        });
    }

    async moveTo(targetX, targetY) {
        response = await this._api.get('/api/get_route_to_position/', {
            data: { target_x: targetX, target_y: targetY },
            successMessage: `Route vers (${targetX}, ${targetY}) calculée avec succès !`,
            errorMessage: `Échec du calcul de la route vers (${targetX}, ${targetY}).`
        });

        console.log('Route calculée :', response.route);


    }
}

const move = new Move();
export { move };
export default move;
import { Api } from "./api.js";

class Move {
    _api = new Api('http://ec2-15-237-116-133.eu-west-3.compute.amazonaws.com:8443/');

    async moveNext(direction) {
        console.log('move next', direction);

        return await this._api.post('/api/move/', {
            data: { direction },
            successMessage: `Déplacement vers ${direction} réussi !`,
            errorMessage: `Échec du déplacement vers ${direction}.`
        });
    }

    async moveTo(targetX, targetY, startPos) {
        let x = startPos.x;
        let y = startPos.y;

        while (x !== targetX || y !== targetY) {
            let direction = "";

            // Logique de direction Nord/Sud
            if (y > targetY) {
                direction += "N";
            } else if (y < targetY) {
                direction += "S";
            }

            // Logique de direction Ouest/Est
            if (x > targetX) {
                direction += "W";
            } else if (x < targetX) {
                direction += "E";
            }

            if (!direction) break;

            try {
                // Appel du déplacement
                const resp = await this.moveNext(direction);

                // On met à jour la position actuelle avec le retour de l'API
                if (resp && resp.position) {
                    x = resp.position.x;
                    y = resp.position.y;

                    console.log(`Position actuelle : (${x}, ${y}), Énergie : ${resp.energy}`);

                    // save_cell(cell)
                } else {
                    console.error("Déplacement impossible ou bloqué");
                    break;
                }

                await new Promise(resolve => setTimeout(resolve, 800));

            } catch (error) {
                console.error("Erreur lors du trajet :", error);
                break;
            }
        }
        console.log("Cible atteinte !");
    }
}

const move = new Move();
export { move };
export default move;
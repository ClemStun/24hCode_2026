import { Api } from "./api.js";

class Boat {
    _api = new Api('http://ec2-15-237-116-133.eu-west-3.compute.amazonaws.com:8443/');

    async nextLevel() {
        console.log(await this._api.get('/ship/next-level/'));
    }
}

const boat = new Boat();
export { boat };
export default boat;
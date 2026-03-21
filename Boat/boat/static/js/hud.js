import { Api } from './api.js';

class Hud {
    _interval = null;
    _api = new Api('http://ec2-15-237-116-133.eu-west-3.compute.amazonaws.com:8443/');
    static _codinggameId = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjb2RpbmdnYW1lIiwic3ViIjoiMDAyNjQyYzItYmJiMS00OTdkLWFiZTItMDU5ZTA2MGJhNzExIiwicm9sZXMiOlsiVVNFUiJdfQ.bTbRXfHkvrBHYexewru3uX7x3j8L-GfMnXzymkxbU2k';
    static _header = { 'codinggame-id': Hud._codinggameId };

    _boisiumBar = document.querySelector('#boisium-bar .bar-frame-text');
    _feroniumBar = document.querySelector('#feronium-bar .bar-frame-text');
    _charboniumBar = document.querySelector('#charbonium-bar .bar-frame-text');
    _goldBar = document.querySelector('#gold-bar .bar-frame-text');

    _resourceMapping = {
        'boisium': this._boisiumBar,
        'feronium': this._feroniumBar,
        'charbonium': this._charboniumBar,
        'gold': this._goldBar
    };

    _movementBar = document.querySelector('#move-progress');
    _movementDetails = document.querySelector('#move-progress-text');
    _levelBar = document.querySelector('#boat-bar .level-bar .level-text');

    init() {
        setInterval(() => this._updateHud(), 2500);
    }

    async _updateHud() {
        const data = await this._api.get('/players/details', { headers: Hud._header });

        data.resources.push({ type: 'gold', quantity: data.money });
        for (const resource of data.resources) {
            const resourceName = resource.type.toLowerCase();
            if (this._resourceMapping[resourceName]) {
                this._resourceMapping[resourceName].textContent = `${resource.quantity}`;
            }
        }

        this._movementBar.style.cssText = `--move-progress: ${data.ship.availableMove} / ${data.ship.level.maxMovement};`;
        this._movementDetails.textContent = `${data.ship.availableMove} / ${data.ship.level.maxMovement}`;
        this._levelBar.textContent = `NIVEAU ${data.ship.level.id}`;
    }

    async onShutdown() {
        await this._api.onShutdown();
        clearInterval(this._interval);
    }
}

const hud = new Hud();
export default hud;
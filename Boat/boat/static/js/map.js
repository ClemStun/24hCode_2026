import Game from "./game.js";

function getNumberOfTiles(containerSize, tileSize) {
    const tileCount = Math.ceil(containerSize / tileSize) + 2;
    if (tileCount % 2 === 0) {
        return tileCount + 1;
    }

    return tileCount;
}

class Map extends Game {
    _container = document.getElementById('game-container');
    _hud = document.getElementById('game-hud');
    _map = document.getElementById('game-map');
    _mapContainer = document.getElementById('map-container');

    _zoomLevel = 3;
    static _tileSize = [20, 40, 64, 80, 96, 128, 192, 256];

    _tiles = [];
    _currentPosition = { x: 0, y: 0, direction: undefined };
    _currentView = { startX: 0, startY: 0, endX: 0, endY: 0 };

    _inMenu = false;
    _menu = document.getElementById('game-menu');
    _handleMoveUpMenuCallback = this._handleMoveUpMenu.bind(this);
    _handleMoveDownMenuCallback = this._handleMoveDownMenu.bind(this);
    _handleActionMenuCallback = this._handleActionMenu.bind(this);

    init(data) {
        super.init();

        this._currentPosition = data.currentPosition || { x: 0, y: 0 };
        for (const tile of data.tiles) {
            this._tiles[tile.y] ??= [];
            this._tiles[tile.y][tile.x] = tile;
        }

        this._mapContainer.addEventListener('click', (event) => {
            if(event.target.classList.contains('map-cell')) {
                document.querySelectorAll('.map-cell.selected').forEach(cell => cell.classList.remove('selected'));
                event.target.classList.add('selected');
            }
        });

        document.addEventListener('game.menu', (event) => {
            this.toggleMenu();
        });

        this.renderMap();
        this.renderBoat();
    }

    renderMap() {
        const tileSize = Map._tileSize[this._zoomLevel];
        this._mapContainer.style.setProperty('--cell-size', `${tileSize}px`);

        const tilesX = getNumberOfTiles(this._container.clientWidth, tileSize);
        const tilesY = getNumberOfTiles(this._container.clientHeight, tileSize);

        const startX = Math.floor(this._currentPosition.x / tileSize) - Math.floor(tilesX / 2);
        const startY = Math.floor(this._currentPosition.y / tileSize) - Math.floor(tilesY / 2);
        const endX = startX + tilesX;
        const endY = startY + tilesY;

        this._currentView = { startX, startY, endX, endY };
        const rows = [];
        for (let y = startY; y < endY; y++) {
            const row = document.createElement('div');
            row.classList.add('map-row');
            rows.push(row);

            for (let x = startX; x < endX; x++) {
                const div = document.createElement('div');
                div.classList.add('map-cell');
                div.setAttribute('data-x', x);
                div.setAttribute('data-y', y);
                row.appendChild(div);

                const tile = this._tiles[y]?.[x];
                if (tile) {
                    div.id = tile.id;
                    div.setAttribute('data-type', tile.type.toLowerCase());
                    div.setAttribute('data-variant', tile.zone);
                }
            }
        }

        this._mapContainer.innerHTML = '';
        rows.forEach(row => this._mapContainer.appendChild(row));

        this._map.scrollTo({
            left: 1.5 * tileSize,
            top: 1.5 * tileSize
        });
    }

    renderBoat() {
        document.querySelectorAll('.boat').forEach(el => el.remove());
        const tile = document.querySelector(`[data-x="${this._currentPosition.x}"][data-y="${this._currentPosition.y}"]`);
        if (tile) {
            tile.classList.add('boat');
            tile.setAttribute('data-type', 'sea');
            if (this._currentPosition.direction) {
                tile.classList.add(`boat-${this._currentPosition.direction}`);
            }
        }
    }

    setCurrentPosition(x, y, direction) {
        this._currentPosition = { x, y, direction };
    }

    onTileChanged(tile) {
        if (!this._tiles[tile.y]) {
            this._tiles[tile.y] = [];
        }
        this._tiles[tile.y][tile.x] = tile;

        if (tile.x < this._currentView.startX || tile.x >= this._currentView.endX) {
            return;
        }

        if (tile.y < this._currentView.startY || tile.y >= this._currentView.endY) {
            return;
        }

        const cell = this._mapContainer.querySelector(`[data-x="${tile.x}"][data-y="${tile.y}"]`);
        if (cell) {
            cell.setAttribute('data-type', tile.type);
            cell.setAttribute('data-variant', tile.zone);
        }
    }

    zoomIn() {
        if (this._zoomLevel < this._tileSize.length - 1) {
            this._zoomLevel++;
            this.renderMap();
        }
    }

    zoomOut() {
        if (this._zoomLevel > 0) {
            this._zoomLevel--;
            this.renderMap();
        }
    }

    toggleMenu(forceState) {
        this._inMenu = forceState ?? !this._inMenu;

        if (this._inMenu) {
            this._menu.style.cssText = '';
            document.addEventListener('game.move_down', this._handleMoveDownMenuCallback);
            document.addEventListener('game.move_up', this._handleMoveUpMenuCallback);
            document.addEventListener('game.action', this._handleActionMenuCallback);
        } else {
            this._menu.style.cssText = 'display: none;';
            document.removeEventListener('game.move_down', this._handleMoveDownMenuCallback);
            document.removeEventListener('game.move_up', this._handleMoveUpMenuCallback);
            document.removeEventListener('game.action', this._handleActionMenuCallback);
        }
    }

    _handleMoveDownMenu() {
        const current = this._menu.querySelector('.current-choice');
        if (current) {
            const next = current.nextElementSibling || this._menu.querySelector('.choice:first-child');
            if (next) {
                current.classList.remove('current-choice');
                next.classList.add('current-choice');
            }
        }
    }

    _handleMoveUpMenu() {
        const current = this._menu.querySelector('.current-choice');
        if (current) {
            const previous = current.previousElementSibling || this._menu.querySelector('.choice:last-child');
            if (previous) {
                current.classList.remove('current-choice');
                previous.classList.add('current-choice');
            }
        }
    }

    _handleActionMenu() {
        const current = this._menu.querySelector('.current-choice');
        if (current) {
            const callbackName = current.getAttribute('data-callback');
            if (typeof this[callbackName] === 'function') {
                this[callbackName]();
            }
        }
    }

    async end() {
        await this.onShutdown();
        window.location.href = '/';
    }

    openOptions() {

    }

    syncTiles() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json,.txt'; // Adapter selon le type de fichier attendu
        input.style.display = 'none';
        document.body.appendChild(input);

        input.addEventListener('change', async (event) => {
            const file = event.target.files[0];
            if (file) {
                const data = new FormData();
                data.append('file', file);
                await this._api.post('/api/tiles/import/', {
                    data: data
                });
            }

            document.body.removeChild(input);
        });

        input.click();
    }
}

const map = new Map();
window.syncTiles = () => map.syncTiles();
window.closeMenu = () => map.toggleMenu(false);

export { map };
export default map;
import { Api } from "./api.js";
import eventSocket from "./event-socket.js";

class Market {
    _api = new Api('http://ec2-15-237-116-133.eu-west-3.compute.amazonaws.com:8443/');
    static _codinggameId = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjb2RpbmdnYW1lIiwic3ViIjoiMDAyNjQyYzItYmJiMS00OTdkLWFiZTItMDU5ZTA2MGJhNzExIiwicm9sZXMiOlsiVVNFUiJdfQ.bTbRXfHkvrBHYexewru3uX7x3j8L-GfMnXzymkxbU2k';
    static _header = { 'codinggame-id': Market._codinggameId };
    static _teamName = "Devosaur";

    _marketModal = document.getElementById('market-modal');
    _offerPagination = this._marketModal.querySelector('#offers-pagination');
    _offerContainer = this._marketModal.querySelector('#offers-container');
    
    _offerModal = document.getElementById('offer-modal');
    _offerResourceInput = this._offerModal.querySelector('#offer-resource');
    _offerQuantityInput = this._offerModal.querySelector('#offer-quantity');
    _offerPriceInput = this._offerModal.querySelector('#offer-price');

    static _resourceMapping = {
        'boisium': 'Boisium',
        'feronium': 'Feronium',
        'charbonium': 'Charbonium'
    };
    static _resourceColorMapping = {
        'boisium': '#71593F',
        'feronium': '#B5B5B5',
        'charbonium': '#3A3D30'
    };

    _offers = [];
    _currentPage = 1;
    _offersPerPage = 4;

    _onPageClickCallback = this._onPageClick.bind(this);
    _onOfferAcceptedCallback = this._onOfferAccepted.bind(this);
    _onOfferPostedCallback = this._onOfferPosted.bind(this);
    _onOfferDeletedCallback = this._onOfferDeleted.bind(this);

    async init() {
        this._offerPagination.addEventListener('click', this._onPageClickCallback);
        eventSocket.on('ACHAT', this._onOfferAcceptedCallback);
        eventSocket.on('OFFRE', this._onOfferPostedCallback);
        eventSocket.on('OFFRE_SUPPRIMEE', this._onOfferDeletedCallback);

        this._offers = await this._api.get('/marketplace/offers', { headers: Market._header });
        this.render();
    }

    render() {
        const pagesCount = Math.ceil(this._offers.length / this._offersPerPage);
        if (pagesCount < this._currentPage) {
            this._currentPage = pagesCount;
            if (pagesCount === 0) {
                this._currentPage = 1;
            }
        }

        const offers = this._offers.slice((this._currentPage - 1) * this._offersPerPage, this._currentPage * this._offersPerPage);
        
        this._offerPagination.innerHTML = '';
        for (let i = 1; i <= pagesCount; i++) {
            this._offerPagination.appendChild(this._getPageContent(i));
        }

        this._offerContainer.innerHTML = '';
        offers.forEach(offer => {
            this._offerContainer.appendChild(this._getOfferContent(offer));
        });
    }

    async acceptOffer(offerId) {
        const quantity = parseInt(document.querySelector(`[id='${offerId}'] .offer-quantity-input`).value);
        await this._api.post(`/marketplace/purchases`, { data: { quantity, offerId }, headers: Market._header });

        const offer = this._offers.find(offer => offer.id === offerId);
        if (offer.quantityIn - quantity <= 0) {
            this._offers = this._offers.filter(offer => offer.id !== offerId);
        } else {
            offer.quantityIn -= quantity;
        }

        this.render();
    }

    async refuseOffer(offerId) {
        await this._api.delete(`/marketplace/offers/${offerId}`, { headers: Market._header });
        this._offers = this._offers.filter(offer => offer.id !== offerId);
        this.render();
    }

    async postOffer() {
        const resource = this._offerResourceInput.value.toUpperCase();
        const quantity = parseInt(this._offerQuantityInput.value);
        const price = parseInt(this._offerPriceInput.value);

        const offer = await this._api.post('/marketplace/offers', {
            data: {
                resourceType: resource,
                quantityIn: quantity,
                pricePerResource: price
            },
            headers: Market._header
        });

        this._offers.push(offer);
        this.render();

        globalThis.closeOffer();
    }

    _changePage(index) {
        this._currentPage = index;
        this.render();
    }

    _getPageContent(index) {
        const page = document.createElement('div');
        page.textContent = index;
        page.classList.add('page');
        if (index === this._currentPage) {
            page.classList.add('current-page');
        }

        return page;
    }

    _getOfferContent(offer) {
        const resourceName = Market._resourceMapping[offer.resourceType.toLowerCase()];
        const div = document.createElement('div');
        div.classList.add('offer');
        div.id = offer.id;

        const deleteButton = offer.owner.name == Market._teamName ? `
            <button class="btn btn-alt btn-icon btn-danger">
                <img src="/static/assets/icons/close.svg" alt="Delete Offer" onclick="refuseOffer('${offer.id}');">
            </button>
        ` : '';
        div.innerHTML = `
            <div class="bar-icon" style="--bar-icon-color: ${Market._resourceColorMapping[offer.resourceType.toLowerCase()]};">
                <img src="/static/assets/icons/resource-icon.svg" alt="${resourceName}" class="bar-icon-img">
            </div>
            <div class="offer-details">
                <div class="offer-title">
                    <div>${offer.quantityIn} ${resourceName}</div>
                    <input type="number" min="0" max="${offer.quantityIn}" value="0" class="offer-quantity-input">
                </div>
                <div class="offer-actions">
                    <div class="offer-quantity btn btn-alt">
                        <img src="/static/assets/icons/resource-icon-bis.svg" alt="Or" class="offer-quantity-icon">
                        <div>${offer.pricePerResource} Or</div>
                    </div>
                    <div class="offer-buttons">
                        <button class="btn btn-alt btn-icon btn-success">
                            <img src="/static/assets/icons/check.svg" class="accept-offer" alt="Accept Offer" onclick="acceptOffer('${offer.id}');">
                        </button>
                        ${deleteButton}
                    </div>
                </div>
            </div>
        `;

        return div;
    }

    _onPageClick(event) {
        if (event.target.classList.contains('page')) {
            this._changePage(parseInt(event.target.textContent));
        }
    }

    _onOfferAccepted(event) {
        const offer = event.message;
        const existingOffer = this._offers.find(o => o.id === offer.id);
        if (existingOffer) {
            existingOffer.quantityIn -= offer.quantity;
            if (existingOffer.quantityIn <= 0) {
                this._offers = this._offers.filter(o => o.id !== offer.id);
            }

            this.render();
        }
    }

    _onOfferPosted(event) {
        const offer = event.message;
        if (!offer.id) {
            return;
        }

        const existingOfferIndex = this._offers.findIndex(o => o.id === offer.id);
        if (existingOfferIndex >= 0) {
            this._offers[existingOfferIndex] = offer;
        } else {
            this._offers.push(offer);
        }

        this.render();
    }

    _onOfferDeleted(event) {
        const offer = event.message;
        this._offers = this._offers.filter(o => o.id !== offer.id);
        this.render();
    }

    onClose() {
        this._offerPagination.removeEventListener('click', this._onPageClickCallback);
        eventSocket.off('ACHAT', this._onOfferAcceptedCallback);
        eventSocket.off('OFFRE', this._onOfferPostedCallback);
        eventSocket.off('OFFRE_SUPPRIMEE', this._onOfferDeletedCallback);
        this._currentPage = 1;
    }

    async onShutdown() {
        this.onClose();
        await this._api.onShutdown();
    }
}

const market = new Market();
window.acceptOffer = (id) => market.acceptOffer(id);
window.refuseOffer = (id) => market.refuseOffer(id);
window.closeMarket = () => {
    market._marketModal.style.cssText = 'display: none;';
    market.onClose();
};
window.showMarket = async () => {
    market._marketModal.style.cssText = '';
    await market.init();
};
window.showOffer = () => {
    market._offerModal.style.cssText = '';
}
window.closeOffer = () => {
    market._offerModal.style.cssText = 'display: none;';
};
window.submitOffer = () => market.postOffer();

export default market;
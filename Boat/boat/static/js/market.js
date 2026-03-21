export function initMarket() {

// Offres injectées par Django
    const offersContainer = document.getElementById('offers');
    const initialOffers = JSON.parse(offersContainer.dataset.offers || '[]');
    const API_BASE = 'http://ec2-15-237-116-133.eu-west-3.compute.amazonaws.com:8443/marketplace';
    const WS_BASE = 'http://localhost:8001/ws';

    const sellBtn = document.getElementById('sellBtn');
    const sellModal = document.getElementById('sellModal');
    const closeModal = document.getElementById('closeModal');
    const resourceSelect = document.getElementById('resourceSelect');
    const confirmSell = document.getElementById('confirmSell');

    const RESOURCE_COLORS = {
    'FERONIUM': '#B5B5B5',
    'Charbonium': '#3A3D30',
    'Boisium': '#71593F'
    // Ajoute d'autres ressources si besoin
    };

    document.querySelector('.market-header .close-market-btn').onclick = () => {
        document.getElementById('market-modal').style.display = 'none';
    };

    sellBtn.onclick = async () => {
    // Récupère les ressources disponibles
    try {
        const resp = await fetch(`${API_BASE.replace('/marketplace','')}/resources`, {
        headers: {
            'codinggame-Id': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjb2RpbmdnYW1lIiwic3ViIjoiMDAyNjQyYzItYmJiMS00OTdkLWFiZTItMDU5ZTA2MGJhNzExIiwicm9sZXMiOlsiVVNFUiJdfQ.bTbRXfHkvrBHYexewru3uX7x3j8L-GfMnXzymkxbU2k'
        }
        });
        const resources = await resp.json();
        resourceSelect.innerHTML = resources.map(r => `<option value="${r.type}">${r.type} (${r.quantity})</option>`).join('');
        sellModal.style.display = 'flex';
    } catch (e) {
        alert('Erreur lors du chargement des ressources');
    }
    };

    closeModal.onclick = () => {
    sellModal.style.display = 'none';
    };

    confirmSell.onclick = async () => {
    const resourceType = resourceSelect.value;
    const quantityIn = parseInt(document.getElementById('sellQty').value, 10);
    const pricePerResource = parseFloat(document.getElementById('sellPrice').value);
    if (!resourceType || isNaN(quantityIn) || quantityIn < 1 || isNaN(pricePerResource) || pricePerResource < 1) {
        alert('Champs invalides');
        return;
    }
    try {
        const resp = await fetch(`${API_BASE}/offers`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'codinggame-Id': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjb2RpbmdnYW1lIiwic3ViIjoiMDAyNjQyYzItYmJiMS00OTdkLWFiZTItMDU5ZTA2MGJhNzExIiwicm9sZXMiOlsiVVNFUiJdfQ.bTbRXfHkvrBHYexewru3uX7x3j8L-GfMnXzymkxbU2k'
        },
        body: JSON.stringify({ resourceType, quantityIn, pricePerResource })
        });
        if (resp.ok) {
        alert('Offre créée !');
        sellModal.style.display = 'none';
        } else {
        alert('Erreur création offre');
        }
    } catch (e) {
        alert('Erreur réseau');
    }
    };

    let offersById = {};

    function renderOffer(offer) {
    let card = document.getElementById(`offer-${offer.id}`);

    if (!card) {
        card = document.createElement('div');
        card.id = `offer-${offer.id}`;
        card.className = 'card';
        offersContainer.prepend(card);
    }

    const color = RESOURCE_COLORS[offer.resourceType.toUpperCase()] || '#71593F';
    card.innerHTML = `
        <div class="bar-icon" style="--bar-icon-color: ${color};">
        <img src="${window.STATIC_URLS.resourceIcon}" alt="${offer.resourceType}" class="bar-icon-img">
        </div>
        <div class="offer-content">
        <div class="offer-row">
            <div class="offer-title">${offer.quantityIn} ${offer.resourceType}</div>
            <input type="number" min="0" max="${offer.quantityIn}" value="0" class="qty-input">
        </div>
        <div class="offer-row">
            <span class="offer-price">${offer.pricePerResource} Or</span>
            <button class="buy">Acheter</button>
            <button class="close-market-btn" style="width: 32px; height: 32px;" title="Supprimer">
            <img src="${window.STATIC_URLS.closeIcon}" alt="Supprimer" />
            </button>
        </div>
        </div>
    `;

    card.querySelector('.buy').onclick = async () => {
        const qty = parseInt(card.querySelector('.qty-input').value, 10);
        if (isNaN(qty) || qty < 1 || qty > offer.quantityIn) {
        alert('Quantité invalide');
        return;
        }
        try {
        const resp = await fetch(`${API_BASE}/purchases`, {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            'codinggame-Id': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjb2RpbmdnYW1lIiwic3ViIjoiMDAyNjQyYzItYmJiMS00OTdkLWFiZTItMDU5ZTA2MGJhNzExIiwicm9sZXMiOlsiVVNFUiJdfQ.bTbRXfHkvrBHYexewru3uX7x3j8L-GfMnXzymkxbU2k'
            },
            body: JSON.stringify({ offerId: offer.id, quantity: qty })
        });
        if (resp.ok) alert('Achat envoyé !');
        else alert('Erreur achat');
        } catch (error) {
        alert('Erreur réseau lors de l\'achat');
        }
    };

    card.querySelector('.delete').onclick = async () => {
        try {
        const resp = await fetch(`${API_BASE}/offers/${offer.id}`, { method: 'DELETE' });
        if (resp.ok) {
            card.remove();
            delete offersById[offer.id];
        } else {
            alert('Erreur suppression');
        }
        } catch (error) {
        alert('Erreur réseau lors de la suppression');
        }
    };
    }

    // Affiche les offres passées par Django
    if (Array.isArray(initialOffers)) {
    initialOffers.forEach(offer => {
        offersById[offer.id] = offer;
        renderOffer(offer);
    });
    }

    // WebSocket pour les updates temps réel
    function handleWSMessage(data) {
    if (data.type === 'OFFRE' || data.type === 'OFFRE_SUPPRIMEE') {
        const offer = data.message;
        offersById[offer.id] = offer;
        renderOffer(offer);
    } else if (data.type === 'ACHAT') {
        const { offerId, quantity } = data.message;
        if (offersById[offerId]) {
        // Si la quantité achetée est inférieure à la quantité disponible
        if (offersById[offerId].quantityIn > quantity) {
            offersById[offerId].quantityIn -= quantity;
            renderOffer(offersById[offerId]);
        } else {
            // Achat total, on supprime la carte
            const card = document.getElementById(`offer-${offerId}`);
            if (card) card.remove();
            delete offersById[offerId];
        }
        }
    }
    }

    if (window.marketWS) {
        window.marketWS.close();
    }

    const ws = new WebSocket(WS_BASE);
    window.marketWS = ws;
    ws.onopen = () => console.log('WebSocket connecté');
    ws.onclose = () => console.log('WebSocket déconnecté');
    ws.onmessage = event => {
        try {
            const data = JSON.parse(event.data);
            handleWSMessage(data);
        } catch (e) {
            console.error('Erreur parsing message WebSocket:', e);
        }
    };
}
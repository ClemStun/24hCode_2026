const container = document.getElementById("offers");

const ws = new WebSocket(`ws://${window.location.host}/ws`);

let offers = {};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === "OFFRE") {
    const offer = data.message;
    offers[offer.id] = offer;
    render();
  }

  if (data.type === "ACHAT") {
    delete offers[data.message.offerId];
    render();
  }
};

function render() {
  container.innerHTML = "";

  Object.values(offers).forEach((offer) => {
    const div = document.createElement("div");
    div.className = "card";

    div.innerHTML = `
      <h2>${offer.resourceType}</h2>
      <p>Quantité : ${offer.quantityIn}</p>
      <p>Prix : ${offer.pricePerResource} 💰</p>
    `;

    container.appendChild(div);
  });
}
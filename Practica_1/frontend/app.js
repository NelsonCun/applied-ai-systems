const API_URL = "http://127.0.0.1:8000/api";

document.addEventListener("DOMContentLoaded", loadCities);

async function loadCities() {
  const response = await fetch(`${API_URL}/cities`);
  const data = await response.json();

  const origin = document.getElementById("origin");
  const destination = document.getElementById("destination");

  origin.innerHTML = "";
  destination.innerHTML = "";

  data.cities.forEach(city => {
    origin.innerHTML += `<option value="${city}">${city}</option>`;
    destination.innerHTML += `<option value="${city}">${city}</option>`;
  });
}

async function searchShortest() {
  clearResults();

  const origin = document.getElementById("origin").value;
  const destination = document.getElementById("destination").value;

  const response = await fetch(`${API_URL}/routes/shortest`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({origin, destination})
  });

  const data = await response.json();

  if (!response.ok) {
    showMessage(data.detail, "error");
    return;
  }

  renderRoutes([data]);
}

async function searchAll() {
  clearResults();

  const origin = document.getElementById("origin").value;
  const destination = document.getElementById("destination").value;

  const response = await fetch(`${API_URL}/routes/all`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({origin, destination})
  });

  const data = await response.json();

  if (!response.ok) {
    showMessage(data.detail, "error");
    return;
  }

  showMessage(`Se encontraron ${data.total_routes} rutas.`, "success");
  renderRoutes(data.routes);
}

async function addCity() {
  const name = document.getElementById("newCity").value;

  const response = await fetch(`${API_URL}/cities`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({name})
  });

  const data = await response.json();

  if (!response.ok) {
    showMessage(data.detail, "error");
    return;
  }

  showMessage(data.message, "success");
  await loadCities();
}

async function addConnection() {
  const origin = document.getElementById("connectionOrigin").value;
  const destination = document.getElementById("connectionDestination").value;
  const distance = parseInt(document.getElementById("connectionDistance").value);

  const response = await fetch(`${API_URL}/connections`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({origin, destination, distance})
  });

  const data = await response.json();

  if (!response.ok) {
    showMessage(data.detail, "error");
    return;
  }

  showMessage(data.message, "success");
  await loadCities();
}

function renderRoutes(routes) {
  const container = document.getElementById("results");

  routes.forEach((item, index) => {
    container.innerHTML += `
      <div class="route-card">
        <h3>Ruta ${index + 1}</h3>
        <p><strong>Recorrido:</strong> ${item.route.join(" → ")}</p>
        <p><strong>Distancia total:</strong> ${item.distance} km</p>
      </div>
    `;
  });
}

function showMessage(text, type) {
  document.getElementById("message").innerHTML = `<p class="${type}">${text}</p>`;
}

function clearResults() {
  document.getElementById("message").innerHTML = "";
  document.getElementById("results").innerHTML = "";
}
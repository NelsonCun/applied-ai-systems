const API_URL = "http://127.0.0.1:8000/api";

document.addEventListener("DOMContentLoaded", async () => {
  await loadCities();
  renderEmptyState();
});

async function loadCities() {
  try {
    const response = await fetch(`${API_URL}/cities`);

    if (!response.ok) {
      throw new Error("No se pudo obtener ciudades");
    }

    const data = await response.json();
    const cities = data.cities || [];

    fillSelect("origin", cities);
    fillSelect("destination", cities);
    fillSelect("connectionOrigin", cities);
    fillSelect("connectionDestination", cities);

  } catch (error) {
    showMessage("No se pudo cargar el listado de ciudades. Verifique que el backend esté encendido.", "error");
  }
}

function fillSelect(elementId, cities) {
  const select = document.getElementById(elementId);

  if (!select) {
    console.error(`No existe el select con id: ${elementId}`);
    return;
  }

  select.innerHTML = "";

  if (cities.length === 0) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No hay ciudades disponibles";
    select.appendChild(option);
    return;
  }

  cities.forEach(city => {
    const option = document.createElement("option");
    option.value = city;
    option.textContent = formatCityName(city);
    select.appendChild(option);
  });
}

async function searchShortest() {
  clearResults();

  const origin = document.getElementById("origin").value;
  const destination = document.getElementById("destination").value;

  if (!validateDifferentCities(origin, destination)) {
    return;
  }

  try {
    const response = await fetch(`${API_URL}/routes/shortest`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ origin, destination })
    });

    const data = await response.json();

    if (!response.ok) {
      showMessage(data.detail || "No se pudo obtener la ruta más corta.", "error");
      renderEmptyState();
      return;
    }

    showMessage("Ruta más corta encontrada correctamente.", "success");
    renderRoutes([data]);

  } catch (error) {
    showMessage("Error de conexión con el backend.", "error");
    renderEmptyState();
  }
}

async function searchAll() {
  clearResults();

  const origin = document.getElementById("origin").value;
  const destination = document.getElementById("destination").value;

  if (!validateDifferentCities(origin, destination)) {
    return;
  }

  try {
    const response = await fetch(`${API_URL}/routes/all`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ origin, destination })
    });

    const data = await response.json();

    if (!response.ok) {
      showMessage(data.detail || "No existen rutas disponibles.", "error");
      renderEmptyState();
      return;
    }

    showMessage(`Se encontraron ${data.total_routes} rutas ordenadas por distancia.`, "success");
    renderRoutes(data.routes);

  } catch (error) {
    showMessage("Error de conexión con el backend.", "error");
    renderEmptyState();
  }
}

async function addCity() {
  const input = document.getElementById("newCity");
  const name = input.value.trim();

  if (!name) {
    showMessage("Ingrese el nombre de la ciudad.", "error");
    return;
  }

  try {
    const response = await fetch(`${API_URL}/cities`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ name })
    });

    const data = await response.json();

    if (!response.ok) {
      showMessage(data.detail || "No se pudo agregar la ciudad.", "error");
      return;
    }

    showMessage(data.message || "Ciudad agregada correctamente.", data.created === false ? "error" : "success");
    input.value = "";

    await loadCities();

  } catch (error) {
    showMessage("Error de conexión con el backend.", "error");
  }
}

async function addConnection() {
  const origin = document.getElementById("connectionOrigin").value;
  const destination = document.getElementById("connectionDestination").value;
  const distanceInput = document.getElementById("connectionDistance");
  const distance = Number(distanceInput.value);

  if (!validateDifferentCities(origin, destination)) {
    return;
  }

  if (!distance || distance <= 0) {
    showMessage("Ingrese una distancia válida mayor a 0.", "error");
    return;
  }

  try {
    const response = await fetch(`${API_URL}/connections`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        origin,
        destination,
        distance
      })
    });

    const data = await response.json();

    if (!response.ok) {
      showMessage(data.detail || "No se pudo agregar la conexión.", "error");
      return;
    }

    showMessage(data.message || "Conexión agregada correctamente.", data.created === false ? "error" : "success");
    distanceInput.value = "";

    await loadCities();

  } catch (error) {
    showMessage("Error de conexión con el backend.", "error");
  }
}

function renderRoutes(routes) {
  const container = document.getElementById("results");
  container.innerHTML = "";

  routes.forEach((item, index) => {
    const card = document.createElement("article");
    card.className = "route-card";

    card.innerHTML = `
      <div class="route-card-header">
        <h4>Ruta ${index + 1}</h4>
        <span class="distance-badge">${item.distance} km</span>
      </div>

      <p class="route-path">
        ${item.route.map(formatCityName).join(" → ")}
      </p>
    `;

    container.appendChild(card);
  });
}

function renderEmptyState() {
  const container = document.getElementById("results");

  container.innerHTML = `
    <div class="empty-state">
      Seleccione una ciudad origen y una ciudad destino para consultar las rutas disponibles.
    </div>
  `;
}

function validateDifferentCities(origin, destination) {
  if (!origin || !destination) {
    showMessage("Debe seleccionar ciudad origen y ciudad destino.", "error");
    renderEmptyState();
    return false;
  }

  if (origin === destination) {
    showMessage("La ciudad origen y destino no pueden ser iguales.", "error");
    renderEmptyState();
    return false;
  }

  return true;
}

function showMessage(text, type) {
  const message = document.getElementById("message");

  message.innerHTML = `
    <div class="notice ${type}">
      ${text}
    </div>
  `;
}

function clearResults() {
  document.getElementById("message").innerHTML = "";
  renderEmptyState();
}

function formatCityName(value) {
  return String(value)
    .replaceAll("_", " ")
    .replace(/\b\w/g, letter => letter.toUpperCase());
}
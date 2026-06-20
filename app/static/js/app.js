const state = {
  graph: null,
  map: null,
  markers: new Map(),
  graphLayer: null,
  routeLayer: null,
  searchMarker: null,
  captureMarker: null,
  captureMode: false,
  selectedProfile: "walk",
  lastRoute: null,
  graphVisible: true,
};

const categoryLabels = {
  academic: "Academic",
  food: "Food",
  hostel: "Hostel",
  service: "Service",
  sports: "Sports",
  landmark: "Landmark",
  place: "Place",
};

document.addEventListener("DOMContentLoaded", async () => {
  lucide.createIcons();
  await loadGraph();
  setupMap();
  populateSelectors();
  drawGraph();
  drawMarkers();
  bindControls();
  fitToGraph();
});

async function loadGraph() {
  const response = await fetch("/api/graph");
  if (!response.ok) {
    throw new Error("Unable to load graph");
  }
  state.graph = await response.json();
}

function setupMap() {
  const center = window.CAMPUS_META.center || { lat: 28.7508153, lng: 77.1162765 };
  const zoom = window.CAMPUS_META.zoom || 16;
  state.map = L.map("map", {
    zoomControl: false,
    preferCanvas: true,
  }).setView([center.lat, center.lng], zoom);

  L.control.zoom({ position: "bottomright" }).addTo(state.map);

  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(state.map);

  state.map.on("click", handleMapClick);
}

function populateSelectors() {
  const sourceSelect = document.querySelector("#sourceSelect");
  const targetSelect = document.querySelector("#targetSelect");
  const sortedNodes = [...state.graph.nodes].sort((a, b) => a.name.localeCompare(b.name));

  for (const node of sortedNodes) {
    sourceSelect.append(new Option(node.name, node.id));
    targetSelect.append(new Option(node.name, node.id));
  }

  sourceSelect.value = "dtu_entrance";
  targetSelect.value = "dtu_library";
}

function drawMarkers() {
  for (const node of state.graph.nodes) {
    const marker = L.marker([node.lat, node.lng], {
      icon: L.divIcon({
        className: "",
        html: `<span class="node-marker category-${node.category || "place"}"></span>`,
        iconSize: [26, 26],
        iconAnchor: [13, 13],
      }),
      title: node.name,
    });

    const category = categoryLabels[node.category] || "Place";
    marker.bindPopup(`<strong>${escapeHtml(node.name)}</strong><br>${category}<br>${node.lat.toFixed(6)}, ${node.lng.toFixed(6)}`);
    marker.addTo(state.map);
    state.markers.set(node.id, marker);
  }
}

function drawGraph() {
  if (state.graphLayer) {
    state.graphLayer.remove();
  }

  state.graphLayer = L.layerGroup();
  for (const edge of state.graph.edges) {
    L.polyline(edge.coordinates, {
      color: "#5f6f68",
      opacity: 0.42,
      weight: 3,
      dashArray: "4 6",
    }).bindTooltip(`${edge.from} to ${edge.to}: ${Math.round(edge.distance_m)} m`).addTo(state.graphLayer);
  }
  state.graphLayer.addTo(state.map);
}

function bindControls() {
  document.querySelector("#routeButton").addEventListener("click", findRoute);
  document.querySelector("#swapButton").addEventListener("click", swapLocations);
  document.querySelector("#fitButton").addEventListener("click", fitToGraph);
  document.querySelector("#toggleGraphButton").addEventListener("click", toggleGraph);
  document.querySelector("#captureButton").addEventListener("click", toggleCaptureMode);
  document.querySelector("#copyNodeButton").addEventListener("click", copyNodeJson);
  document.querySelector("#downloadGraphButton").addEventListener("click", downloadGraph);
  document.querySelector("#copyTraceButton").addEventListener("click", copyTrace);
  document.querySelector("#searchButton").addEventListener("click", searchPlace);
  document.querySelector("#placeSearch").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      searchPlace();
    }
  });

  for (const button of document.querySelectorAll(".segment")) {
    button.addEventListener("click", () => {
      document.querySelectorAll(".segment").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      state.selectedProfile = button.dataset.profile;
      if (state.lastRoute) {
        findRoute();
      }
    });
  }
}

async function findRoute() {
  const source = document.querySelector("#sourceSelect").value;
  const target = document.querySelector("#targetSelect").value;

  const response = await fetch("/api/route", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source, target, profile: state.selectedProfile }),
  });

  const payload = await response.json();
  if (!response.ok) {
    renderRouteError(payload.error || "Unable to find route");
    return;
  }

  state.lastRoute = payload;
  renderRoute(payload);
  renderTrace(payload);
}

function renderRoute(route) {
  if (state.routeLayer) {
    state.routeLayer.remove();
  }

  state.routeLayer = L.polyline(route.coordinates, {
    color: "#167a5b",
    weight: 7,
    opacity: 0.92,
    lineCap: "round",
    lineJoin: "round",
  }).addTo(state.map);

  state.map.fitBounds(state.routeLayer.getBounds(), { padding: [42, 42] });

  document.querySelector("#timeMetric").textContent = `${route.total_time_min.toFixed(1)} min`;
  document.querySelector("#distanceMetric").textContent = formatDistance(route.total_distance_m);
  document.querySelector("#stopsMetric").textContent = route.path.length;

  const steps = document.querySelector("#routeSteps");
  steps.replaceChildren();
  route.edges.forEach((edge, index) => {
    const item = document.createElement("li");
    item.innerHTML = `<strong>${escapeHtml(edge.from_name)}</strong> to <strong>${escapeHtml(edge.to_name)}</strong><br><span>${formatDistance(edge.distance_m)} · ${edge.time_min.toFixed(1)} min</span>`;
    steps.append(item);
  });
}

function renderTrace(route) {
  const visitedText = route.visited_order.map((item, index) => `${index + 1}. ${item.name}`).join("  ");
  document.querySelector("#visitedOrder").textContent = visitedText || "No nodes settled.";

  const traceList = document.querySelector("#traceList");
  traceList.replaceChildren();

  for (const step of route.trace) {
    const item = document.createElement("article");
    item.className = "trace-item";
    const relaxations = step.relaxations.length
      ? step.relaxations.map((relaxation) => `${relaxation.to_name}: ${formatNullableTime(relaxation.old_time_min)} -> ${relaxation.new_time_min.toFixed(2)} min`).join("; ")
      : "No shorter neighbors found.";

    item.innerHTML = `<strong>${escapeHtml(step.current_name)} settled at ${step.settled_time_min.toFixed(2)} min</strong><p>${escapeHtml(relaxations)}</p>`;
    traceList.append(item);
  }
}

function renderRouteError(message) {
  document.querySelector("#timeMetric").textContent = "--";
  document.querySelector("#distanceMetric").textContent = "--";
  document.querySelector("#stopsMetric").textContent = "--";
  document.querySelector("#routeSteps").replaceChildren();
  document.querySelector("#visitedOrder").textContent = message;
  document.querySelector("#traceList").replaceChildren();
}

function swapLocations() {
  const source = document.querySelector("#sourceSelect");
  const target = document.querySelector("#targetSelect");
  const value = source.value;
  source.value = target.value;
  target.value = value;
  if (state.lastRoute) {
    findRoute();
  }
}

function toggleGraph() {
  state.graphVisible = !state.graphVisible;
  document.querySelector("#toggleGraphButton").classList.toggle("active", state.graphVisible);

  if (state.graphVisible) {
    state.graphLayer.addTo(state.map);
  } else {
    state.graphLayer.remove();
  }
}

function fitToGraph() {
  const latLngs = state.graph.nodes.map((node) => [node.lat, node.lng]);
  state.map.fitBounds(L.latLngBounds(latLngs), { padding: [38, 38] });
}

function toggleCaptureMode() {
  state.captureMode = !state.captureMode;
  document.querySelector("#captureButton").classList.toggle("active", state.captureMode);
}

function handleMapClick(event) {
  if (!state.captureMode) {
    return;
  }

  const { lat, lng } = event.latlng;
  if (state.captureMarker) {
    state.captureMarker.remove();
  }

  state.captureMarker = L.marker([lat, lng], {
    icon: L.divIcon({
      className: "",
      html: '<span class="node-marker category-custom"></span>',
      iconSize: [26, 26],
      iconAnchor: [13, 13],
    }),
  }).addTo(state.map);

  const node = {
    id: `node_${Date.now()}`,
    name: "New Campus Location",
    lat: Number(lat.toFixed(7)),
    lng: Number(lng.toFixed(7)),
    category: "custom",
  };
  document.querySelector("#nodeOutput").textContent = JSON.stringify(node, null, 2);
}

async function searchPlace() {
  const input = document.querySelector("#placeSearch");
  const status = document.querySelector("#searchStatus");
  const query = input.value.trim();
  if (query.length < 3) {
    status.textContent = "Enter at least 3 characters.";
    return;
  }

  status.textContent = "Searching...";
  const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
  const payload = await response.json();

  if (!response.ok || payload.error) {
    status.textContent = payload.error || "Search failed.";
    return;
  }

  if (!payload.results.length) {
    status.textContent = "No results found.";
    return;
  }

  const result = payload.results[0];
  status.textContent = result.display_name;
  state.map.setView([result.lat, result.lng], 17);

  if (state.searchMarker) {
    state.searchMarker.remove();
  }

  state.searchMarker = L.marker([result.lat, result.lng]).addTo(state.map);
  state.searchMarker.bindPopup(`<strong>${escapeHtml(result.name)}</strong><br>${escapeHtml(result.display_name)}`).openPopup();
}

async function copyNodeJson() {
  const text = document.querySelector("#nodeOutput").textContent;
  await navigator.clipboard.writeText(text);
}

async function copyTrace() {
  if (!state.lastRoute) {
    return;
  }
  const lines = [];
  lines.push(`Path: ${state.lastRoute.path.map((node) => node.name).join(" -> ")}`);
  lines.push(`Total time: ${state.lastRoute.total_time_min} min`);
  lines.push(`Total distance: ${state.lastRoute.total_distance_m} m`);
  lines.push("Visited order:");
  state.lastRoute.visited_order.forEach((node, index) => lines.push(`${index + 1}. ${node.name}`));
  await navigator.clipboard.writeText(lines.join("\n"));
}

function downloadGraph() {
  const blob = new Blob([JSON.stringify(state.graph, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "campus_graph.json";
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function formatDistance(meters) {
  if (meters >= 1000) {
    return `${(meters / 1000).toFixed(2)} km`;
  }
  return `${Math.round(meters)} m`;
}

function formatNullableTime(value) {
  if (value === null || value === undefined) {
    return "inf";
  }
  return `${Number(value).toFixed(2)} min`;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

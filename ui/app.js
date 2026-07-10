import { applyFilters, facetCounts } from "./filter.js";

const els = {
  profile: document.getElementById("profile"),
  region: document.getElementById("region"),
  load: document.getElementById("load"),
  filter: document.getElementById("filter"),
  facets: document.getElementById("facets"),
  tbody: document.getElementById("tbody"),
  status: document.getElementById("status"),
  banner: document.getElementById("banner"),
  arnHeader: document.getElementById("arn-header"),
};

const state = {
  arns: [],
  activeServices: new Set(),
  source: null, // EventSource while a load is in flight
  sortAsc: null, // null = API order, true/false = sorted
};

function setStatus(text, isError = false) {
  els.status.textContent = text;
  els.status.classList.toggle("error", isError);
}

function setLoading(loading) {
  els.profile.disabled = loading;
  els.region.disabled = loading;
  els.load.textContent = loading ? "Cancel" : "Load";
}

function render() {
  const shown = applyFilters(state.arns, els.filter.value, state.activeServices);
  if (state.sortAsc !== null) {
    shown.sort((a, b) => state.sortAsc ? a.localeCompare(b) : b.localeCompare(a));
  }
  els.tbody.replaceChildren(...shown.map((arn) => {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.textContent = arn;
    tr.append(td);
    return tr;
  }));
  if (state.arns.length > 0) {
    setStatus(`Done! (${state.arns.length} resources, ${shown.length} shown)`);
  }
}

function renderFacets() {
  els.facets.replaceChildren(...facetCounts(state.arns).map(([service, count]) => {
    const chip = document.createElement("button");
    chip.className = "chip" + (state.activeServices.has(service) ? " active" : "");
    chip.textContent = `${service} (${count})`;
    chip.onclick = () => {
      if (state.activeServices.has(service)) {
        state.activeServices.delete(service);
      } else {
        state.activeServices.add(service);
      }
      renderFacets();
      render();
    };
    return chip;
  }));
}

function cancelLoad() {
  if (state.source) {
    state.source.close();
    state.source = null;
  }
  setLoading(false);
}

function clearTable() {
  cancelLoad();
  state.arns = [];
  state.activeServices.clear();
  state.sortAsc = null;
  els.filter.value = "";
  renderFacets();
  els.tbody.replaceChildren();
  setStatus("Select profile and region, then click Load");
}

function startLoad() {
  clearTable();
  setLoading(true);
  setStatus("Loading …");
  const params = new URLSearchParams({
    profile: els.profile.value,
    region: els.region.value.split(" ")[0],
  });
  const source = new EventSource(`/api/resources?${params}`);
  state.source = source;

  source.addEventListener("progress", (event) => {
    setStatus(`Loading … ${JSON.parse(event.data).count} resources`);
  });

  source.addEventListener("done", (event) => {
    state.arns = JSON.parse(event.data).arns;
    cancelLoad();
    renderFacets();
    render();
  });

  // Fires for BOTH our custom `event: error` SSE messages (which carry
  // .data) and transport-level failures (which don't) — hence the check.
  source.addEventListener("error", (event) => {
    if (!state.source) return; // already handled by done/cancel
    const message = event.data
      ? JSON.parse(event.data).message
      : "Connection to local server lost";
    cancelLoad();
    setStatus(`Error: ${message}`, true);
  });
}

async function init() {
  const [profiles, regions] = await Promise.all([
    fetch("/api/profiles").then((r) => r.json()),
    fetch("/api/regions").then((r) => r.json()),
  ]);
  if (profiles.length === 0) els.banner.hidden = false;
  els.profile.append(...profiles.map((p) => new Option(p, p)));
  els.region.append(...regions.map((r) => new Option(r, r)));
  setStatus("Select profile and region, then click Load");
}

els.load.onclick = () => {
  if (state.source) {
    cancelLoad();
    setStatus("Load cancelled");
  } else {
    startLoad();
  }
};
els.filter.oninput = render;
els.profile.onchange = clearTable;
els.region.onchange = clearTable;
els.arnHeader.onclick = () => {
  state.sortAsc = state.sortAsc === null ? true : !state.sortAsc;
  render();
};

init();

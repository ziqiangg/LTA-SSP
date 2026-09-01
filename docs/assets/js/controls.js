(function () {
  "use strict";

  var DATA_BASE = "../assets/data/";
  var CATALOG_LABEL = {
    cybersecurity: "Cybersecurity",
    dss: "Digital Service Standards"
  };
  var LEVEL_LABEL = { 0: "Mandatory", 1: "Baseline", 2: "Optional" };

  var typeSelect = document.getElementById("type-select");
  var levelFilter = document.getElementById("level-filter");
  var domainFilter = document.getElementById("domain-filter");
  var searchInput = document.getElementById("search-input");
  var resultCount = document.getElementById("result-count");
  var controlList = document.getElementById("control-list");

  if (!typeSelect) return;

  var controls = [];
  var domains = [];
  var systemTypes = [];
  var profiles = {};
  var domainsById = {};
  var systemTypesById = {};

  var state = {
    type: "",
    levels: new Set(),
    domains: new Set(),
    q: ""
  };

  function parseInitialState() {
    var params = new URLSearchParams(location.search);
    state.type = params.get("type") || "";
    var levelParam = params.get("level");
    if (levelParam) {
      levelParam.split(",").forEach(function (l) {
        var n = parseInt(l, 10);
        if (!isNaN(n)) state.levels.add(n);
      });
    }
    var domainParam = params.get("domain");
    if (domainParam) {
      domainParam.split(",").forEach(function (d) {
        if (d) state.domains.add(d);
      });
    }
    state.q = params.get("q") || "";
  }

  function syncUrl() {
    var params = new URLSearchParams();
    if (state.type) params.set("type", state.type);
    if (state.levels.size) params.set("level", Array.from(state.levels).sort().join(","));
    if (state.domains.size) params.set("domain", Array.from(state.domains).sort().join(","));
    if (state.q) params.set("q", state.q);
    var qs = params.toString();
    history.replaceState(null, "", qs ? "?" + qs : location.pathname);
  }

  function isCatalogMode() {
    return state.type.indexOf("catalog:") === 0;
  }

  function activeCatalog() {
    if (isCatalogMode()) return state.type.slice("catalog:".length);
    var t = systemTypesById[state.type];
    return t ? t.catalog : null;
  }

  function levelsAvailable() {
    if (isCatalogMode() || !state.type) return [];
    var t = systemTypesById[state.type];
    return t ? t.levelsAvailable : [];
  }

  function domainsUsed() {
    var catalog = activeCatalog();
    if (!catalog) return [];
    if (isCatalogMode()) {
      return domains.filter(function (d) { return d.catalog === catalog; }).map(function (d) { return d.id; });
    }
    var t = systemTypesById[state.type];
    return t ? t.domainsUsed : [];
  }

  function defaultLevelsFor(typeId) {
    var t = systemTypesById[typeId];
    if (!t) return new Set();
    var defaults = t.levelsAvailable.filter(function (l) { return l === 0 || l === 1; });
    if (!defaults.length) defaults = t.levelsAvailable.slice();
    return new Set(defaults);
  }

  function workingControls() {
    if (!state.type) return [];
    if (isCatalogMode()) {
      var catalog = state.type.slice("catalog:".length);
      return controls
        .filter(function (c) { return c.catalog === catalog; })
        .map(function (c) { return Object.assign({}, c, { level: null }); });
    }
    var profile = profiles[state.type];
    if (!profile) return [];
    var levelById = {};
    profile.forEach(function (e) { levelById[e.controlId] = e.level; });
    return controls
      .filter(function (c) { return Object.prototype.hasOwnProperty.call(levelById, c.id); })
      .map(function (c) { return Object.assign({}, c, { level: levelById[c.id] }); });
  }

  function applyFilters() {
    var list = workingControls();
    if (!isCatalogMode() && state.levels.size) {
      list = list.filter(function (c) { return state.levels.has(c.level); });
    }
    if (state.domains.size) {
      list = list.filter(function (c) { return state.domains.has(c.domainId); });
    }
    if (state.q) {
      var q = state.q.toLowerCase();
      list = list.filter(function (c) {
        return (
          c.id.toLowerCase().indexOf(q) !== -1 ||
          c.title.toLowerCase().indexOf(q) !== -1 ||
          (c.description && c.description.toLowerCase().indexOf(q) !== -1)
        );
      });
    }
    list.sort(function (a, b) { return a.id.localeCompare(b.id, undefined, { numeric: true }); });
    return list;
  }

  function renderTypeOptions() {
    typeSelect.innerHTML = "";
    var placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "— Select a system type —";
    typeSelect.appendChild(placeholder);

    var typesGroup = document.createElement("optgroup");
    typesGroup.label = "System types";
    systemTypes.forEach(function (t) {
      var opt = document.createElement("option");
      opt.value = t.id;
      opt.textContent = t.name;
      typesGroup.appendChild(opt);
    });
    typeSelect.appendChild(typesGroup);

    var catalogGroup = document.createElement("optgroup");
    catalogGroup.label = "Full catalogs (no level filter)";
    [["catalog:cybersecurity", "All Cybersecurity Controls"], ["catalog:dss", "All Digital Service Standards Controls"]].forEach(function (pair) {
      var opt = document.createElement("option");
      opt.value = pair[0];
      opt.textContent = pair[1];
      catalogGroup.appendChild(opt);
    });
    typeSelect.appendChild(catalogGroup);

    typeSelect.value = state.type;
  }

  function renderLevelFilter() {
    levelFilter.innerHTML = "";
    if (!state.type) {
      var msg = document.createElement("span");
      msg.className = "control-guidance";
      msg.textContent = "Select a system type first.";
      levelFilter.appendChild(msg);
      return;
    }
    if (isCatalogMode()) {
      var note = document.createElement("span");
      note.className = "control-guidance";
      note.textContent = "Level applicability depends on system type — pick one above to filter by level.";
      levelFilter.appendChild(note);
      return;
    }
    var available = levelsAvailable();
    [0, 1, 2].forEach(function (lvl) {
      var id = "level-check-" + lvl;
      var label = document.createElement("label");
      label.className = "level-check";
      label.htmlFor = id;

      var input = document.createElement("input");
      input.type = "checkbox";
      input.id = id;
      input.value = lvl;

      var badge = document.createElement("span");
      badge.className = "level-chip";
      badge.dataset.level = lvl;
      badge.setAttribute("aria-hidden", "true");
      badge.textContent = "L" + lvl;

      var text = document.createElement("span");
      text.textContent = LEVEL_LABEL[lvl];

      var isAvailable = available.indexOf(lvl) !== -1;
      if (!isAvailable) {
        input.disabled = true;
        badge.classList.add("is-unavailable");
        label.title = "Level " + lvl + " does not apply to this system type";
      } else {
        input.checked = state.levels.has(lvl);
        input.addEventListener("change", function () {
          if (input.checked) state.levels.add(lvl);
          else state.levels.delete(lvl);
          renderResults();
          syncUrl();
        });
      }

      label.appendChild(input);
      label.appendChild(badge);
      label.appendChild(text);
      levelFilter.appendChild(label);
    });
  }

  function renderDomainFilter() {
    domainFilter.innerHTML = "";
    if (!state.type) return;
    var catalog = activeCatalog();
    var used = new Set(domainsUsed());
    var catalogDomains = domains.filter(function (d) { return d.catalog === catalog; });
    catalogDomains.forEach(function (d) {
      var id = "domain-check-" + d.id;
      var label = document.createElement("label");
      label.className = "domain-check";
      label.htmlFor = id;

      var input = document.createElement("input");
      input.type = "checkbox";
      input.id = id;
      input.value = d.id;

      var swatch = document.createElement("span");
      swatch.className = "domain-swatch";
      swatch.setAttribute("aria-hidden", "true");
      swatch.style.setProperty("--swatch-color", "var(--domain-" + d.id + ")");

      var code = document.createElement("span");
      code.className = "domain-code";
      code.textContent = d.id;

      var name = document.createElement("span");
      name.className = "domain-name";
      name.textContent = d.name;

      var isUsed = isCatalogMode() || used.has(d.id);
      if (!isUsed) {
        input.disabled = true;
        label.title = d.name + " — not used by this system type";
      } else {
        input.checked = state.domains.has(d.id);
        input.addEventListener("change", function () {
          if (input.checked) state.domains.add(d.id);
          else state.domains.delete(d.id);
          renderResults();
          syncUrl();
        });
      }

      label.appendChild(input);
      label.appendChild(swatch);
      label.appendChild(code);
      label.appendChild(name);
      domainFilter.appendChild(label);
    });
  }

  function levelChipHtml(level) {
    if (level === null || level === undefined) return "";
    return '<span class="level-chip" data-level="' + level + '">L' + level + "</span>";
  }

  function domainTagHtml(domainId, catalog) {
    var d = domainsById[domainId];
    var name = d ? d.name : domainId;
    return (
      '<span class="domain-tag" data-catalog="' + catalog + '" style="--tag-color: var(--domain-' + domainId + ')" title="' +
      escapeHtml(name) +
      '">' +
      domainId +
      "</span>"
    );
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function renderControlCard(c) {
    var li = document.createElement("li");
    var details = document.createElement("details");
    details.className = "control-card";

    var summary = document.createElement("summary");
    summary.innerHTML =
      '<span class="control-id">' + c.id + "</span>" +
      '<span class="control-title">' + escapeHtml(c.title) + "</span>" +
      levelChipHtml(c.level) +
      domainTagHtml(c.domainId, c.catalog);
    details.appendChild(summary);

    var body = document.createElement("div");
    body.className = "control-body";

    var desc = document.createElement("p");
    desc.textContent = c.description || "";
    body.appendChild(desc);

    if (c.guidance) {
      var guidance = document.createElement("p");
      guidance.className = "control-guidance";
      guidance.textContent = c.guidance;
      body.appendChild(guidance);
    }

    if (c.parameters && c.parameters.length) {
      var table = document.createElement("table");
      table.innerHTML =
        "<thead><tr><th>Parameter</th><th>Type</th><th>Description</th></tr></thead><tbody>" +
        c.parameters
          .map(function (p) {
            return (
              "<tr><td>" + escapeHtml(p.id) + "</td><td>" + escapeHtml(p.type) + "</td><td>" + escapeHtml(p.description) + "</td></tr>"
            );
          })
          .join("") +
        "</tbody>";
      body.appendChild(table);
    }

    if (c.citations && c.citations.length) {
      var cite = document.createElement("p");
      cite.className = "control-guidance";
      cite.appendChild(document.createTextNode("References: "));
      c.citations.forEach(function (ci, i) {
        if (i) cite.appendChild(document.createTextNode(", "));
        var label = ci.standard + (ci.reference ? " (" + ci.reference + ")" : "");
        // Citations scraped from an upstream hyperlink carry the real href; ones
        // recovered from prose don't, and stay as plain text.
        if (ci.url) {
          var a = document.createElement("a");
          a.href = ci.url;
          a.textContent = label;
          a.rel = "noopener noreferrer";
          a.target = "_blank";
          cite.appendChild(a);
        } else {
          cite.appendChild(document.createTextNode(label));
        }
      });
      body.appendChild(cite);
    }

    details.appendChild(body);
    li.appendChild(details);
    return li;
  }

  function renderResults() {
    controlList.innerHTML = "";
    if (!state.type) {
      resultCount.textContent = "Select a system type or catalog above to see its controls.";
      return;
    }
    var filtered = applyFilters();
    resultCount.textContent = filtered.length + " control" + (filtered.length === 1 ? "" : "s");
    var frag = document.createDocumentFragment();
    filtered.forEach(function (c) { frag.appendChild(renderControlCard(c)); });
    controlList.appendChild(frag);
  }

  function onTypeChange() {
    state.type = typeSelect.value;
    state.domains = new Set();
    state.levels = isCatalogMode() || !state.type ? new Set() : defaultLevelsFor(state.type);
    renderLevelFilter();
    renderDomainFilter();
    renderResults();
    syncUrl();
  }

  var searchDebounce;
  function onSearchInput() {
    clearTimeout(searchDebounce);
    searchDebounce = setTimeout(function () {
      state.q = searchInput.value;
      renderResults();
      syncUrl();
    }, 150);
  }

  function init() {
    Promise.all([
      fetch(DATA_BASE + "controls.json").then(function (r) { return r.json(); }),
      fetch(DATA_BASE + "domains.json").then(function (r) { return r.json(); }),
      fetch(DATA_BASE + "system-types.json").then(function (r) { return r.json(); }),
      fetch(DATA_BASE + "profiles.json").then(function (r) { return r.json(); })
    ])
      .then(function (results) {
        controls = results[0];
        domains = results[1];
        systemTypes = results[2];
        profiles = results[3];
        domains.forEach(function (d) { domainsById[d.id] = d; });
        systemTypes.forEach(function (t) { systemTypesById[t.id] = t; });

        parseInitialState();
        if (!state.levels.size && state.type && !isCatalogMode() && !new URLSearchParams(location.search).get("level")) {
          state.levels = defaultLevelsFor(state.type);
        }

        renderTypeOptions();
        renderLevelFilter();
        renderDomainFilter();
        searchInput.value = state.q;
        renderResults();

        typeSelect.addEventListener("change", onTypeChange);
        searchInput.addEventListener("input", onSearchInput);
      })
      .catch(function (err) {
        resultCount.textContent = "Couldn't load control data. Try reloading the page.";
        console.error(err);
      });
  }

  init();
})();

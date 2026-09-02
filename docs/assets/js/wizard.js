(function () {
  "use strict";

  // Tick-all-that-apply baseline builder (ADR-001 step 1), replacing the old single-
  // outcome q1-q7 tree. A system can be more than one thing at once (a public digital
  // service that also uses Generative AI, say) — this composes a baseline from
  // independent characteristics instead of forcing one exclusive path. Composition
  // itself (union + high-water-mark level resolution) happens in controls.js, which
  // accepts a comma-joined list of system-type ids; this file only decides which ids
  // to send it, and surfaces the two conflict cases ADR-001 says to flag rather than
  // silently resolve.

  var TYPE_NAMES = {
    "low-risk-cloud": "Low-Risk Cloud",
    "low-risk-on-premises": "Low-Risk On-Premises",
    "medium-risk-cloud": "Medium-Risk Cloud",
    "high-risk-cloud": "High-Risk Cloud CII",
    "generative-ai": "Generative AI",
    "sandbox": "Sandbox",
    "digital-services-others": "Digital Services (Others)",
    "digital-services-high-impact": "Digital Services (High Impact)"
  };

  // Ordered ladder from F-005/F-012: sandbox, low- and medium-risk-cloud share the same
  // 117-control membership (differing only in per-control level); high-risk-cloud adds
  // 20 more. Ticking several is "unsure, cast a wider net" — controls.js's high-water-
  // mark merge takes the strictest level wherever the same control appears more than
  // once, so composing several rungs never loses information.
  var RUNGS = [
    { id: "sandbox", type: "sandbox", label: "Sandbox", hint: "Pilot or demonstration only — no production data." },
    { id: "low", type: "low-risk-cloud", label: "Low", hint: "Up to Restricted, Sensitive Normal." },
    { id: "medium", type: "medium-risk-cloud", label: "Medium", hint: "Confidential, Sensitive High." },
    { id: "high", type: "high-risk-cloud", label: "High / CII", hint: "Confidential, Sensitive High, and Critical Information Infrastructure." }
  ];

  var app = document.getElementById("wizard-app");
  if (!app) return;

  var state = {
    hosting: "", // "on-premises" | "cloud" | ""
    rungs: new Set(),
    genai: false,
    ds: "" // "" | "others" | "high-impact"
  };

  function parseInitialState() {
    var p = new URLSearchParams(location.search);
    state.hosting = p.get("hosting") || "";
    var rungParam = p.get("rungs");
    if (rungParam) {
      rungParam.split(",").forEach(function (r) { if (r) state.rungs.add(r); });
    }
    state.genai = p.get("genai") === "1";
    state.ds = p.get("ds") || "";
  }

  function syncUrl() {
    var p = new URLSearchParams();
    if (state.hosting) p.set("hosting", state.hosting);
    if (state.rungs.size) p.set("rungs", Array.from(state.rungs).sort().join(","));
    if (state.genai) p.set("genai", "1");
    if (state.ds) p.set("ds", state.ds);
    var qs = p.toString();
    history.replaceState(null, "", qs ? "?" + qs : location.pathname);
  }

  // Resolves current ticks to either: { incomplete: true } (nothing decidable yet),
  // { blocked: "..." } (a combination ADR-001 says to flag, not compute), or
  // { types: [...], notes: [...] } (a composable baseline, plus advisory notes).
  function resolve() {
    var types = [];
    var notes = [];

    if (state.hosting === "on-premises") {
      if (state.rungs.size) {
        return {
          blocked:
            "On-premises and a cloud sensitivity rung were both ticked. The SSP defines only " +
            "one on-premises template — it doesn't branch by sensitivity the way the cloud " +
            "tiers do — so this combination can't be composed. Untick one."
        };
      }
      types.push("low-risk-on-premises");
    } else if (state.hosting === "cloud") {
      if (!state.rungs.size) return { incomplete: true };
      if (state.rungs.has("sandbox") && state.rungs.has("high")) {
        return {
          blocked:
            "Sandbox and High/CII were both ticked. There's no upstream-defined “CII " +
            "sandbox” profile — these are the two ends of the same ladder, with " +
            "nothing composed in between (F-012). Pick whichever is the closer real answer: " +
            "Sandbox if this is genuinely a pilot with no production or CII data, High-Risk " +
            "Cloud CII if compliance actually requires it."
        };
      }
      RUNGS.forEach(function (r) { if (state.rungs.has(r.id)) types.push(r.type); });
    }

    if (state.genai) {
      types.push("generative-ai");
      if (state.rungs.has("high")) {
        notes.push(
          "Generative AI's own classification caps at “Up to Confidential, Sensitive " +
          "High” — combining it with High-Risk Cloud CII is a combination this tool " +
          "doesn't resolve. Treat the composed list as a starting point, not a certified answer."
        );
      }
    }
    if (state.ds === "others") types.push("digital-services-others");
    if (state.ds === "high-impact") types.push("digital-services-high-impact");

    if (!types.length) return { incomplete: true };
    return { types: types, notes: notes };
  }

  function el(tag, className, text) {
    var e = document.createElement(tag);
    if (className) e.className = className;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function renderChoiceGroup(container, name, options, checkedTest, onChange, type) {
    options.forEach(function (opt) {
      var id = name + "-" + opt.value;
      var label = el("label", "choice-option");
      label.htmlFor = id;

      var input = el("input");
      input.type = type;
      input.name = name;
      input.id = id;
      input.value = opt.value;
      input.checked = checkedTest(opt.value);
      input.addEventListener("change", function () { onChange(opt.value, input.checked); });

      var text = el("span", null, opt.label);
      label.appendChild(input);
      label.appendChild(text);
      if (opt.hint) label.appendChild(el("span", "choice-hint", opt.hint));
      container.appendChild(label);
    });
  }

  function renderResolution() {
    var result = resolve();
    var box = el("div", "wizard-result-box");

    if (result.incomplete) {
      box.appendChild(el("p", "placeholder-note", "Tick at least one option above to see a computed baseline."));
      app.appendChild(box);
      return;
    }

    if (result.blocked) {
      box.appendChild(el("p", "wizard-conflict", result.blocked));
      app.appendChild(box);
      return;
    }

    var names = result.types.map(function (t) { return TYPE_NAMES[t] || t; });
    var heading = el("h2", null, names.join(" + "));
    box.appendChild(heading);

    if (result.types.length > 1) {
      box.appendChild(el(
        "p",
        "control-guidance",
        "Composed baseline (ADR-001): every control from each of the above, most-stringent level wins where they overlap."
      ));
    }

    result.notes.forEach(function (n) {
      box.appendChild(el("p", "placeholder-note", n));
    });

    var typeParam = result.types.join(",");
    var grid = el("div", "wizard-result");
    var ul = el("ul", "card-grid");

    var controlsLink = document.createElement("a");
    controlsLink.className = "nav-card";
    controlsLink.href = "../controls/?type=" + encodeURIComponent(typeParam);
    controlsLink.innerHTML =
      '<span class="nav-card-title">See its controls, with status and reason &rarr;</span>' +
      '<span class="nav-card-meta">Every catalog control, tagged in-profile or not — nothing silently filtered.</span>';
    var li1 = document.createElement("li");
    li1.appendChild(controlsLink);
    ul.appendChild(li1);

    result.types.forEach(function (tid) {
      var a = document.createElement("a");
      a.className = "nav-card";
      a.href = "../system-types/" + tid + "/";
      a.innerHTML =
        '<span class="nav-card-title">Read the ' + (TYPE_NAMES[tid] || tid) + ' profile &rarr;</span>' +
        '<span class="nav-card-meta">Classification criteria, domains, and control levels used.</span>';
      var li = document.createElement("li");
      li.appendChild(a);
      ul.appendChild(li);
    });

    grid.appendChild(ul);
    box.appendChild(grid);
    app.appendChild(box);
  }

  function render() {
    app.innerHTML = "";

    // --- Hosting location ---
    var hostingFieldset = el("fieldset");
    hostingFieldset.appendChild(el("legend", null, "Where is it hosted?"));
    var hostingList = el("div", "check-list");
    renderChoiceGroup(
      hostingList,
      "hosting",
      [
        { value: "cloud", label: "Cloud", hint: "Hosted through a third-party Cloud Service Provider." },
        { value: "on-premises", label: "On-premises", hint: "The standard defines only one on-premises template." }
      ],
      function (v) { return state.hosting === v; },
      function (v, checked) {
        state.hosting = checked ? v : "";
        if (v !== "cloud") state.rungs.clear();
        render();
        syncUrl();
      },
      "radio"
    );
    hostingFieldset.appendChild(hostingList);
    app.appendChild(hostingFieldset);

    // --- Cloud sensitivity rung (only once "cloud" is chosen) ---
    if (state.hosting === "cloud") {
      var rungFieldset = el("fieldset");
      rungFieldset.appendChild(el("legend", null, "Sensitivity rung — tick one, or several if unsure"));
      var rungList = el("div", "check-list");
      renderChoiceGroup(
        rungList,
        "rung",
        RUNGS.map(function (r) { return { value: r.id, label: r.label, hint: r.hint }; }),
        function (v) { return state.rungs.has(v); },
        function (v, checked) {
          if (checked) state.rungs.add(v);
          else state.rungs.delete(v);
          render();
          syncUrl();
        },
        "checkbox"
      );
      rungFieldset.appendChild(rungList);
      app.appendChild(rungFieldset);
    }

    // --- Generative AI overlay ---
    var genaiFieldset = el("fieldset");
    genaiFieldset.appendChild(el("legend", null, "Does it incorporate Generative AI as a core function?"));
    var genaiList = el("div", "check-list");
    renderChoiceGroup(
      genaiList,
      "genai",
      [{ value: "1", label: "Yes — add the Generative AI overlay", hint: "" }],
      function () { return state.genai; },
      function (v, checked) {
        state.genai = checked;
        render();
        syncUrl();
      },
      "checkbox"
    );
    genaiFieldset.appendChild(genaiList);
    app.appendChild(genaiFieldset);

    // --- Digital service overlay ---
    var dsFieldset = el("fieldset");
    dsFieldset.appendChild(el("legend", null, "Is it a public-facing digital service tracked under WOGAA?"));
    var dsList = el("div", "check-list");
    renderChoiceGroup(
      dsList,
      "ds",
      [
        { value: "others", label: "Yes — fewer than 1,000,000 visits/year", hint: "" },
        { value: "high-impact", label: "Yes — 1,000,000+ visits/year", hint: "" }
      ],
      function (v) { return state.ds === v; },
      function (v, checked) {
        state.ds = checked ? v : "";
        render();
        syncUrl();
      },
      "radio"
    );
    dsFieldset.appendChild(dsList);
    app.appendChild(dsFieldset);

    renderResolution();

    var nav = el("div", "wizard-nav");
    var reset = document.createElement("a");
    reset.href = "#";
    reset.className = "source-link";
    reset.textContent = "← Reset";
    reset.addEventListener("click", function (e) {
      e.preventDefault();
      state = { hosting: "", rungs: new Set(), genai: false, ds: "" };
      render();
      syncUrl();
    });
    nav.appendChild(reset);

    var skip = document.createElement("a");
    skip.href = "../";
    skip.className = "source-link";
    skip.textContent = "Not sure — show me all 8 types";
    nav.appendChild(skip);

    app.appendChild(nav);
  }

  parseInitialState();
  render();
})();

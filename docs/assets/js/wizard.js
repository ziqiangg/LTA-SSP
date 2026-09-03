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
  //
  // Fetches system-types.json (ADR-001 amendment, ADR-005) to source every option's
  // display name and classification text live, rather than duplicating them as
  // hardcoded strings that can silently drift from the corpus (RQ-2 issue 5). Never
  // fetches controls.json/domains.json/profiles.json — composition stays controls.js's
  // job.
  //
  // CII designation is its own tick (ADR-005), not folded into the sensitivity rung:
  // medium-risk-cloud and high-risk-cloud have byte-for-byte identical
  // classificationText in the corpus, so sensitivity alone cannot distinguish them —
  // only CII designation does (RQ-2 issue 3).
  //
  // Leaving "Where is it hosted?" unanswered no longer dead-ends the sensitivity
  // question (ADR-007): ticking a sensitivity rung with hosting blank composes the
  // relevant cloud tier(s) together with the single on-premises baseline, since
  // on-premises doesn't branch by sensitivity either (F-004 issue 2). This is the
  // same "compose conservatively under disclosed uncertainty" idiom ADR-005 already
  // uses for CII, extended one axis further — RQ-6's baseline run (F-013) found 8 of
  // 15 pilot cases dead-ended here specifically, breaking this tool's own stated
  // "tick more than one if unsure" contract for exactly the one axis that had no
  // hedge affordance at all.
  //
  // Also fetches level-definitions.json (F-003) to show the standard's own
  // selectionGuidance sentence on every computed result — this tool constructs a
  // starting baseline, and F-003 found the standard's one line on how selection is
  // actually meant to work was committed to the corpus but shown to nobody.

  var DATA_BASE = "../assets/data/";

  var app = document.getElementById("wizard-app");
  if (!app) return;

  var systemTypesById = {};
  var levelDefinitions = {};

  // Ordered ladder from F-005/F-012: sandbox and low-risk-cloud share the same
  // 117-control membership as the sensitive band's medium-risk-cloud reading (differing
  // only in per-control level); high-risk-cloud adds 20 more on top of that. Ticking
  // several is "unsure, cast a wider net" — controls.js's high-water-mark merge takes
  // the strictest level wherever the same control appears more than once, so composing
  // several rungs never loses information. "sensitive" has no single `type` — see
  // cloudTierTypes(), which resolves it against state.cii.
  var RUNGS = [
    { id: "sandbox", type: "sandbox", label: "Sandbox" },
    { id: "low", type: "low-risk-cloud", label: "Low" },
    { id: "sensitive", hintType: "medium-risk-cloud", label: "Confidential, Sensitive High" }
  ];

  var state = {
    hosting: "", // "on-premises" | "cloud" | ""
    rungs: new Set(),
    cii: "", // "" (unanswered) | "yes" | "no" — only meaningful when rungs has "sensitive"
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
    var ciiParam = p.get("cii");
    state.cii = (ciiParam === "yes" || ciiParam === "no") ? ciiParam : "";
    state.genai = p.get("genai") === "1";
    state.ds = p.get("ds") || "";
  }

  function syncUrl() {
    var p = new URLSearchParams();
    if (state.hosting) p.set("hosting", state.hosting);
    if (state.rungs.size) p.set("rungs", Array.from(state.rungs).sort().join(","));
    if (state.cii) p.set("cii", state.cii);
    if (state.genai) p.set("genai", "1");
    if (state.ds) p.set("ds", state.ds);
    var qs = p.toString();
    history.replaceState(null, "", qs ? "?" + qs : location.pathname);
  }

  // Resolves the cloud-hosting rungs (plus CII, for the "sensitive" band) to a list of
  // system-type ids. Unanswered CII on a ticked "sensitive" band hedges by including
  // both medium- and high-risk-cloud, rather than forcing a third click — F-010 found
  // 0/15 realistic descriptions state CII designation, so "unsure" is the common case,
  // not an edge one.
  function cloudTierTypes() {
    var types = [];
    if (state.rungs.has("sandbox")) types.push("sandbox");
    if (state.rungs.has("low")) types.push("low-risk-cloud");
    if (state.rungs.has("sensitive")) {
      if (state.cii === "yes") types.push("high-risk-cloud");
      else if (state.cii === "no") types.push("medium-risk-cloud");
      else { types.push("medium-risk-cloud"); types.push("high-risk-cloud"); }
    }
    return types;
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
    } else if (state.hosting === "cloud" && !state.rungs.size) {
      return { incomplete: true };
    }

    // Cloud sensitivity rungs resolve the same way whether hosting is
    // explicitly "cloud" or genuinely unanswered (F-013/ADR-007): "I don't
    // know if this is cloud or on-premises, but I know the data is
    // sensitive" has an honest answer. Composes the relevant cloud tier(s)
    // and, when hosting is blank and a non-sandbox rung was ticked, the
    // single on-premises baseline too — on-premises doesn't branch by
    // sensitivity either (F-004 issue 2). Sandbox is excluded from this
    // hedge: F-012 found no on-premises sandbox profile exists upstream to
    // hedge toward.
    if (state.hosting !== "on-premises" && state.rungs.size) {
      var cloudTypes = cloudTierTypes();
      if (state.rungs.has("sandbox") && cloudTypes.indexOf("high-risk-cloud") !== -1) {
        return {
          blocked:
            "Sandbox and CII-designated were both ticked (or CII was left unanswered, which " +
            "hedges toward it). There's no upstream-defined “CII sandbox” profile — these are " +
            "the two ends of the same ladder, with nothing composed in between (F-012). Pick " +
            "whichever is the closer real answer: Sandbox if this is genuinely a pilot with no " +
            "production or CII data, or answer CII directly above if compliance actually requires it."
        };
      }
      types = types.concat(cloudTypes);
      if (state.hosting === "" && (state.rungs.has("low") || state.rungs.has("sensitive"))) {
        types.push("low-risk-on-premises");
        notes.push(
          "Hosting not specified — composing the relevant cloud tier(s) together with the " +
          "single on-premises baseline, since sensitivity level doesn't change the " +
          "on-premises profile. Answer “Where is it hosted?” above for a narrower result."
        );
      }
    }

    if (state.rungs.has("sensitive") && state.cii === "") {
      notes.push(
        "CII designation left unanswered — composing both Medium- and High-Risk Cloud CII to " +
        "stay conservative until you know."
      );
    }

    if (state.genai) {
      types.push("generative-ai");
      if (types.indexOf("high-risk-cloud") !== -1) {
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

  function typeName(id) {
    return (systemTypesById[id] && systemTypesById[id].name) || id;
  }

  function classificationText(id) {
    return (systemTypesById[id] && systemTypesById[id].classificationText) || "";
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

    var names = result.types.map(typeName);
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

    // F-003: the composed list above is this tool's own construction, not an
    // upstream determination — the standard's one sentence on how controls
    // are actually meant to be selected belongs right where that baseline is
    // handed over, not left in the unfetched level-definitions.json.
    if (levelDefinitions.selectionGuidance) {
      var guidance = el("p", "control-guidance", levelDefinitions.selectionGuidance + " — ");
      var link = document.createElement("a");
      link.className = "source-link";
      link.href = levelDefinitions.sourceUrl;
      link.textContent = "the official standard";
      guidance.appendChild(link);
      guidance.appendChild(document.createTextNode("."));
      box.appendChild(guidance);
    }

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
        '<span class="nav-card-title">Read the ' + typeName(tid) + ' profile &rarr;</span>' +
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
    // render() rebuilds the whole fieldset tree from scratch on every tick, which drops
    // keyboard focus to <body> unless it's explicitly restored — every input id is
    // deterministic (name + "-" + value) and stable across re-renders, so re-focusing by
    // id after rebuilding puts a keyboard user back where they were instead of ejecting
    // them to the top of the form (site-critic finding, 2026-09-02).
    var focusedId = document.activeElement && document.activeElement.id;
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
        if (v !== "cloud") { state.rungs.clear(); state.cii = ""; }
        render();
        syncUrl();
      },
      "radio"
    );
    hostingFieldset.appendChild(hostingList);
    if (!state.hosting) {
      hostingFieldset.appendChild(el(
        "p",
        "placeholder-note",
        "Not sure, or a third party manages it? Leave both unticked — ticking a sensitivity " +
        "band below will still give you a combined baseline covering the relevant cloud tier " +
        "and the single on-premises profile."
      ));
    }
    app.appendChild(hostingFieldset);

    // --- Cloud sensitivity rung (once "cloud" is chosen, or hosting is left
    // unanswered — F-013/ADR-007: ticking a rung with hosting blank still
    // resolves to an honest combined baseline, see resolve()) ---
    if (state.hosting !== "on-premises") {
      var rungFieldset = el("fieldset");
      rungFieldset.appendChild(el("legend", null, "Sensitivity rung — tick one, or several if unsure"));
      var rungList = el("div", "check-list");
      renderChoiceGroup(
        rungList,
        "rung",
        RUNGS.map(function (r) {
          return { value: r.id, label: r.label, hint: classificationText(r.hintType || r.type) };
        }),
        function (v) { return state.rungs.has(v); },
        function (v, checked) {
          if (checked) state.rungs.add(v);
          else state.rungs.delete(v);
          if (v === "sensitive" && !checked) state.cii = "";
          render();
          syncUrl();
        },
        "checkbox"
      );
      rungFieldset.appendChild(rungList);
      app.appendChild(rungFieldset);
    }

    // --- CII designation (only once the "sensitive" band is ticked) ---
    if (state.hosting !== "on-premises" && state.rungs.has("sensitive")) {
      var ciiFieldset = el("fieldset");
      ciiFieldset.appendChild(el("legend", null, "Is this system designated Critical Information Infrastructure (CII)?"));
      var ciiList = el("div", "check-list");
      renderChoiceGroup(
        ciiList,
        "cii",
        [
          { value: "yes", label: "Yes — CII-designated", hint: "" },
          { value: "no", label: "No — not CII-designated", hint: "" }
        ],
        function (v) { return state.cii === v; },
        function (v, checked) {
          state.cii = checked ? v : "";
          render();
          syncUrl();
        },
        "radio"
      );
      ciiFieldset.appendChild(ciiList);
      if (!state.cii) {
        ciiFieldset.appendChild(el(
          "p",
          "placeholder-note",
          "Not sure? Leave both unticked — the composed baseline will include both Medium- and " +
          "High-Risk Cloud CII controls until you know."
        ));
      }
      app.appendChild(ciiFieldset);
    }

    // --- Generative AI overlay ---
    var genaiFieldset = el("fieldset");
    genaiFieldset.appendChild(el("legend", null, "Does it incorporate Generative AI as a core function?"));
    var genaiList = el("div", "check-list");
    renderChoiceGroup(
      genaiList,
      "genai",
      [{
        value: "1",
        label: "Yes — add the Generative AI overlay",
        hint: classificationText("generative-ai")
      }],
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
        {
          value: "others",
          label: "Yes — fewer than 1,000,000 visits/year",
          hint: classificationText("digital-services-others")
        },
        {
          value: "high-impact",
          label: "Yes — 1,000,000+ visits/year",
          hint: classificationText("digital-services-high-impact")
        }
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
      state = { hosting: "", rungs: new Set(), cii: "", genai: false, ds: "" };
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

    if (focusedId) {
      var toFocus = document.getElementById(focusedId);
      if (toFocus) toFocus.focus();
    }
  }

  app.textContent = "Loading…";
  Promise.all([
    fetch(DATA_BASE + "system-types.json").then(function (r) { return r.json(); }),
    fetch(DATA_BASE + "level-definitions.json").then(function (r) { return r.json(); })
  ])
    .then(function (results) {
      results[0].forEach(function (t) { systemTypesById[t.id] = t; });
      levelDefinitions = results[1];
      parseInitialState();
      render();
    })
    .catch(function () {
      app.textContent = "Couldn't load system-type data. Try reloading the page.";
    });
})();

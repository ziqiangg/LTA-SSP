(function () {
  "use strict";

  var RESULT_NAMES = {
    "low-risk-cloud": "Low-Risk Cloud",
    "low-risk-on-premises": "Low-Risk On-Premises",
    "medium-risk-cloud": "Medium-Risk Cloud",
    "high-risk-cloud": "High-Risk Cloud CII",
    "generative-ai": "Generative AI",
    "sandbox": "Sandbox",
    "digital-services-others": "Digital Services (Others)",
    "digital-services-high-impact": "Digital Services (High Impact)"
  };

  var RESULT_NOTES = {
    "low-risk-on-premises":
      "Note: the SSP standard only defines one on-premises profile. If your on-premises system is Medium or High sensitivity, this is still the closest official template — check the official page directly.",
    "sandbox":
      "Note: Sandbox is a pilot/demonstration profile — it uses only Level 0 and Level 2 controls (no Level 1)."
  };

  var TREE = {
    q1: {
      question: "Is this a public-facing digital service tracked under Whole‑of‑Government Application Analytics (WOGAA) and is not an internal/back-office system?",
      options: [
        { label: "Yes", next: "q2" },
        { label: "No", next: "q3" }
      ]
    },
    q2: {
      question: "Does it receive at least 1,000,000 visits per year (per WOGAA traffic statistics)?",
      options: [
        { label: "Yes, 1,000,000+ visits/year", next: "digital-services-high-impact" },
        { label: "No, fewer than 1,000,000 visits/year", next: "digital-services-others" }
      ]
    },
    q3: {
      question: "Does the system incorporate Generative AI as a core function?",
      options: [
        { label: "Yes", next: "generative-ai" },
        { label: "No", next: "q4" }
      ]
    },
    q4: {
      question: "Is this a sandbox or non-production pilot environment only?",
      options: [
        { label: "Yes, sandbox/pilot only", next: "sandbox" },
        { label: "No, it's a production system", next: "q5" }
      ]
    },
    q5: {
      question: "Is it designated Critical Information Infrastructure (CII), or otherwise Confidential/Sensitive High and cloud-hosted?",
      options: [
        { label: "Yes", next: "high-risk-cloud" },
        { label: "No", next: "q6" }
      ]
    },
    q6: {
      question: "Is it hosted on-premises, or on the cloud?",
      options: [
        { label: "On-premises", next: "low-risk-on-premises" },
        { label: "Cloud", next: "q7" }
      ]
    },
    q7: {
      question: "What's its agency-assessed Security Sensitivity Level?",
      options: [
        { label: "Low — up to Restricted, Sensitive Normal", next: "low-risk-cloud" },
        { label: "Medium — Confidential, Sensitive High", next: "medium-risk-cloud" }
      ]
    }
  };

  var app = document.getElementById("wizard-app");
  if (!app) return;

  var history = []; // stack of {nodeId, answerLabel}
  var current = "q1";

  function isResult(nodeId) {
    return Object.prototype.hasOwnProperty.call(RESULT_NAMES, nodeId);
  }

  function render() {
    app.innerHTML = "";

    if (isResult(current)) {
      renderResult(current);
      return;
    }

    var node = TREE[current];
    var stepNum = history.length + 1;

    var progress = document.createElement("span");
    progress.className = "wizard-progress";
    progress.textContent = "Step " + stepNum;
    app.appendChild(progress);

    var h2 = document.createElement("h2");
    h2.textContent = node.question;
    app.appendChild(h2);

    var list = document.createElement("ul");
    list.className = "wizard-options";
    node.options.forEach(function (opt) {
      var li = document.createElement("li");
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "wizard-option";
      btn.textContent = opt.label;
      btn.addEventListener("click", function () {
        history.push({ nodeId: current, answerLabel: opt.label });
        current = opt.next;
        render();
      });
      li.appendChild(btn);
      list.appendChild(li);
    });
    app.appendChild(list);

    var nav = document.createElement("div");
    nav.className = "wizard-nav";

    if (history.length > 0) {
      var back = document.createElement("a");
      back.href = "#";
      back.className = "source-link";
      back.textContent = "← Back";
      back.addEventListener("click", function (e) {
        e.preventDefault();
        var prev = history.pop();
        current = prev.nodeId;
        render();
      });
      nav.appendChild(back);
    } else {
      nav.appendChild(document.createElement("span"));
    }

    var skip = document.createElement("a");
    skip.href = "../";
    skip.className = "source-link";
    skip.textContent = "Not sure — show me all 8 types";
    nav.appendChild(skip);

    app.appendChild(nav);
  }

  function renderResult(typeId) {
    var name = RESULT_NAMES[typeId];

    var progress = document.createElement("span");
    progress.className = "wizard-progress";
    progress.textContent = "Result";
    app.appendChild(progress);

    var h2 = document.createElement("h2");
    h2.textContent = name;
    app.appendChild(h2);

    if (history.length > 0) {
      var p = document.createElement("p");
      p.className = "control-guidance";
      var summary = history.map(function (h) { return h.answerLabel; }).join(" → ");
      p.textContent = "Based on: " + summary;
      app.appendChild(p);
    }

    if (RESULT_NOTES[typeId]) {
      var note = document.createElement("p");
      note.className = "placeholder-note";
      note.textContent = RESULT_NOTES[typeId];
      app.appendChild(note);
    }

    var grid = document.createElement("div");
    grid.className = "wizard-result";

    var ul = document.createElement("ul");
    ul.className = "card-grid";

    var profileLink = document.createElement("a");
    profileLink.className = "nav-card";
    profileLink.href = "../system-types/" + typeId + "/";
    profileLink.innerHTML =
      '<span class="nav-card-title">Read the ' + name + ' profile &rarr;</span>' +
      '<span class="nav-card-meta">Classification criteria, domains, and control levels used.</span>';
    var li1 = document.createElement("li");
    li1.appendChild(profileLink);
    ul.appendChild(li1);

    var controlsLink = document.createElement("a");
    controlsLink.className = "nav-card";
    controlsLink.href = "../controls/?type=" + typeId;
    controlsLink.innerHTML =
      '<span class="nav-card-title">See its controls &rarr;</span>' +
      '<span class="nav-card-meta">Pre-filtered to ' + name + ' in the control browser.</span>';
    var li2 = document.createElement("li");
    li2.appendChild(controlsLink);
    ul.appendChild(li2);

    grid.appendChild(ul);
    app.appendChild(grid);

    var nav = document.createElement("div");
    nav.className = "wizard-nav";
    var back = document.createElement("a");
    back.href = "#";
    back.className = "source-link";
    back.textContent = "← Start over";
    back.addEventListener("click", function (e) {
      e.preventDefault();
      history = [];
      current = "q1";
      render();
    });
    nav.appendChild(back);
    app.appendChild(nav);
  }

  render();
})();

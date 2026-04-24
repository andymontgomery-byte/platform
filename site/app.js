(function () {
  const state = {
    standards: [],
    dictionary: null,
    posture: "all",
    search: "",
    privacy: "all"
  };

  const decisions = [
    {
      title: "Canonical Data Model",
      question: "Should each 1EdTech spec become its own isolated schema?",
      choice: "Use a canonical relational education graph with standard-specific projections.",
      tradeoff: "Developers get normal joins across roster, standards, content, events, and credentials, but the platform must maintain conformance views and adapters per standard version."
    },
    {
      title: "SQL Contract",
      question: "Should developers see raw tables or curated SQL views?",
      choice: "Expose raw tables plus stable documented views.",
      tradeoff: "Power users and AI agents can inspect lineage, while app builders get stable contracts that survive internal schema changes."
    },
    {
      title: "Identifiers",
      question: "Should source-system IDs become primary keys?",
      choice: "Use internal UUIDs plus a first-class identifier crosswalk.",
      tradeoff: "The platform stays stable when SIS, LMS, assessment, or credential IDs change, but every public surface must explain which ID belongs to which system."
    },
    {
      title: "Assessment Content",
      question: "Should QTI be fully decomposed into relational tables?",
      choice: "Store package artifacts and project searchable fields.",
      tradeoff: "The platform avoids accidentally becoming a brittle assessment engine, while still supporting search, alignment, validation, accessibility metadata, and reporting."
    },
    {
      title: "Learning Activity",
      question: "Should activity be current state or append-only event history?",
      choice: "Store immutable Caliper events and curated projections.",
      tradeoff: "Analytics keeps the original event truth, while product dashboards and AI agents can query safer summary tables."
    },
    {
      title: "Tool Integration",
      question: "Is LTI enough for app developers?",
      choice: "Use LTI 1.3/LTI Advantage for launch, membership, deep linking, and grades, plus OAuth-scoped platform APIs for deeper data access.",
      tradeoff: "Vendors get familiar launch workflows and richer normalized data, but scopes must prevent launch context from becoming broad data access."
    },
    {
      title: "Privacy and Security",
      question: "Can privacy be added after the model is useful?",
      choice: "Treat 1EdTech Security Framework, Data Privacy, TrustEd Apps, and least privilege as architecture inputs.",
      tradeoff: "This slows early modeling, but education data requires tenant isolation, audit logs, scopes, consent, retention, and field-level classification from the start."
    },
    {
      title: "Documentation",
      question: "Should docs be hand-written separately from the schema?",
      choice: "Use a governed data dictionary as a source artifact for SQL, OpenAPI, Markdown, examples, and AI-readable context.",
      tradeoff: "Every change has documentation cost, but SQL and JSON surfaces stay consistent and understandable."
    }
  ];

  const apiGroups = [
    ["/organizations", "Districts, schools, departments, and other education organizations."],
    ["/people", "Learners, teachers, staff, guardians where permitted, and role/context data."],
    ["/academic-sessions", "Calendars, terms, courses, classes, sections, and enrollments."],
    ["/standards", "CASE frameworks, items, associations, rubrics, and crosswalks."],
    ["/resources", "Content metadata, cartridge imports, resource allocation, and standards alignment."],
    ["/assessments", "QTI packages, items, tests, metadata, accessibility, validation, and alignment."],
    ["/gradebook", "Line items, categories, score scales, results, assessment results, and LTI AGS bridges."],
    ["/events", "Caliper ingestion, event queries, projections, aggregates, and privacy-safe analytics."],
    ["/lti", "Tool registrations, deployments, launches, deep linking, NRPS, and AGS helpers."],
    ["/credentials", "Open Badges, CLR records, issuers, endorsements, verification, and status."],
    ["/dictionary", "Machine-readable descriptions for every table, field, endpoint, enum, and relationship."]
  ];

  const guide = {
    provides: [
      "Roster, organization, course, class, and enrollment context normalized from OneRoster.",
      "CASE standards and competency graph for alignment, search, reporting, and AI reasoning.",
      "QTI package storage with searchable projections, validation status, accessibility metadata, and lineage.",
      "Caliper event ingestion with immutable history and safer projections for analytics.",
      "LTI 1.3 launch, LTI Advantage grade, roster, and deep-linking workflows.",
      "Credential foundations for Open Badges 3.0 and CLR 2.0."
    ],
    owns: [
      "The learning experience, pedagogy, content authoring, tutoring logic, or assessment runtime inside the app.",
      "User interface quality, accessibility of the app, and workflow design for educators and learners.",
      "Clear data minimization: request only the scopes and fields the app needs.",
      "Standard-specific certification for provider surfaces the app itself claims.",
      "Customer-specific configuration, support, and implementation services."
    ],
    path: [
      "Register the app and request scoped access for the smallest useful data set.",
      "Use LTI 1.3 for launch and classroom context when the app is opened from a course.",
      "Read dictionary metadata before consuming an API field or SQL view.",
      "Join roster, CASE alignment, QTI metadata, Caliper activity, and gradebook data through platform IDs and documented crosswalks.",
      "Write results, events, credentials, or package imports back through standards-aware endpoints."
    ]
  };

  const roadmap = [
    ["Phase 0", "Standards Corpus and Dictionary Seed", "Versioned standards registry, first dictionary schema, source links, Markdown docs, SQL schema, and OpenAPI stub."],
    ["Phase 1", "OneRoster Core", "Tenants, organizations, users, sessions, courses, classes, enrollments, identifiers, CSV import/export, and basic gradebook."],
    ["Phase 2", "CASE Backbone", "Frameworks, items, associations, rubrics, definitions, versions, crosswalks, and alignment APIs."],
    ["Phase 3", "QTI Assessment Repository", "QTI 3 package storage, searchable projections, validation, Data-SSML support, and QTI 2.2 migration path."],
    ["Phase 4", "Caliper Event Platform", "Caliper 1.2 ingestion, immutable envelopes, profile-specific projections, and privacy-safe aggregates."],
    ["Phase 5", "LTI Developer Platform", "LTI 1.3 launch validation, registrations, deployments, AGS, NRPS, Deep Linking, sandbox tenants, and scopes."],
    ["Phase 6", "Content and Credentials", "Common Cartridge, Thin Common Cartridge, Open Badges 3.0, CLR 2.0, Edu-API preparation, and Uniform ID support."]
  ];

  document.addEventListener("DOMContentLoaded", init);

  async function init() {
    setupCanvas();
    renderStaticSections();
    await loadData();
    bindFilters();
    renderAll();
  }

  async function loadData() {
    try {
      const [standardsResponse, dictionaryResponse] = await Promise.all([
        fetch("../data/standards-registry.seed.json"),
        fetch("../data/data-dictionary.seed.json")
      ]);
      const standardsData = await standardsResponse.json();
      const dictionaryData = await dictionaryResponse.json();
      state.standards = standardsData.standards || [];
      state.dictionary = dictionaryData;
    } catch (error) {
      console.warn("Could not load seed data. Rendering fallback content.", error);
      state.standards = [];
      state.dictionary = { privacy_classes: [], objects: [] };
    }
  }

  function bindFilters() {
    const search = document.getElementById("dictionarySearch");
    const privacy = document.getElementById("privacyFilter");

    search.addEventListener("input", function (event) {
      state.search = event.target.value.trim().toLowerCase();
      renderDictionary();
    });

    privacy.addEventListener("change", function (event) {
      state.privacy = event.target.value;
      renderDictionary();
    });
  }

  function renderAll() {
    renderMetrics();
    renderPostureFilters();
    renderStandards();
    renderPrivacyFilter();
    renderDictionary();
  }

  function renderMetrics() {
    const objects = state.dictionary.objects || [];
    const fields = objects.reduce(function (total, object) {
      return total + ((object.fields && object.fields.length) || 0);
    }, 0);
    setText("metricStandards", String(state.standards.length));
    setText("metricObjects", String(objects.length));
    setText("metricFields", String(fields));
  }

  function renderPostureFilters() {
    const host = document.getElementById("postureFilters");
    const postures = ["all"].concat(unique(state.standards.map(function (standard) {
      return standard.platform_posture;
    }).filter(Boolean)));

    host.innerHTML = "";
    postures.forEach(function (posture) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = posture === "all" ? "All" : titleCase(posture);
      button.className = posture === state.posture ? "active" : "";
      button.addEventListener("click", function () {
        state.posture = posture;
        renderPostureFilters();
        renderStandards();
      });
      host.appendChild(button);
    });
  }

  function renderStandards() {
    const host = document.getElementById("standardsGrid");
    const standards = state.standards.filter(function (standard) {
      return state.posture === "all" || standard.platform_posture === state.posture;
    });

    host.innerHTML = "";
    standards.forEach(function (standard) {
      const card = document.createElement("article");
      card.className = "standard-card";
      card.innerHTML = [
        '<div class="card-top">',
        "<h3>" + escapeHtml(standard.name) + "</h3>",
        '<span class="pill">' + escapeHtml(titleCase(standard.platform_posture || "tracked")) + "</span>",
        "</div>",
        '<p class="standard-meta">' + escapeHtml(standard.latest_public_status_found || "Status tracked") + "</p>",
        "<p>" + escapeHtml(standard.platform_role || standard.plain_description || "") + "</p>",
        '<div class="source-list">' + renderSourceLinks(standard.sources || []) + "</div>"
      ].join("");
      host.appendChild(card);
    });
  }

  function renderPrivacyFilter() {
    const select = document.getElementById("privacyFilter");
    const classes = state.dictionary.privacy_classes || [];
    classes.forEach(function (privacyClass) {
      const option = document.createElement("option");
      option.value = privacyClass.privacy_class;
      option.textContent = titleCase(privacyClass.privacy_class);
      select.appendChild(option);
    });
  }

  function renderDictionary() {
    const host = document.getElementById("dictionaryObjects");
    const objects = (state.dictionary.objects || []).filter(matchesDictionaryFilter).slice(0, 9);
    host.innerHTML = "";

    if (!objects.length) {
      host.innerHTML = '<article class="dictionary-card"><h3>No matches</h3><p>Try another term or privacy class.</p></article>';
      return;
    }

    objects.forEach(function (object) {
      const card = document.createElement("article");
      card.className = "dictionary-card";
      const fields = (object.fields || []).slice(0, 3).map(function (field) {
        return [
          '<div class="field-row">',
          "<code>" + escapeHtml(field.technical_name || field.field_key) + "</code>",
          "<span>" + escapeHtml(field.plain_description || "") + "</span>",
          "</div>"
        ].join("");
      }).join("");

      card.innerHTML = [
        '<div class="card-top">',
        "<h3>" + escapeHtml(object.name) + "</h3>",
        '<span class="pill">' + escapeHtml(titleCase(object.privacy_class || "tracked")) + "</span>",
        "</div>",
        "<p>" + escapeHtml(object.plain_description || "") + "</p>",
        '<div class="field-list">' + fields + "</div>"
      ].join("");
      host.appendChild(card);
    });
  }

  function matchesDictionaryFilter(object) {
    const privacyOk = state.privacy === "all" || object.privacy_class === state.privacy ||
      (object.fields || []).some(function (field) {
        return field.privacy_class === state.privacy;
      });

    if (!privacyOk) {
      return false;
    }

    if (!state.search) {
      return true;
    }

    const haystack = [
      object.object_key,
      object.domain_key,
      object.name,
      object.plain_description,
      object.why_it_exists,
      object.source_standard
    ].concat((object.fields || []).flatMap(function (field) {
      return [
        field.field_key,
        field.technical_name,
        field.plain_description,
        field.school_example,
        field.common_mistakes
      ];
    })).join(" ").toLowerCase();

    return haystack.includes(state.search);
  }

  function renderStaticSections() {
    renderDecisions();
    renderApiGroups();
    renderGuide();
    renderRoadmap();
  }

  function renderDecisions() {
    const host = document.getElementById("decisionList");
    host.innerHTML = decisions.map(function (decision) {
      return [
        '<article class="decision-card">',
        "<h3>" + escapeHtml(decision.title) + "</h3>",
        "<dl>",
        "<div><dt>Question</dt><dd>" + escapeHtml(decision.question) + "</dd></div>",
        "<div><dt>Choice</dt><dd>" + escapeHtml(decision.choice) + "</dd></div>",
        "<div><dt>Tradeoff</dt><dd>" + escapeHtml(decision.tradeoff) + "</dd></div>",
        "</dl>",
        "</article>"
      ].join("");
    }).join("");
  }

  function renderApiGroups() {
    const host = document.getElementById("apiGrid");
    host.innerHTML = apiGroups.map(function (group) {
      return [
        '<article class="api-card">',
        '<span class="api-path">' + escapeHtml(group[0]) + "</span>",
        "<p>" + escapeHtml(group[1]) + "</p>",
        "</article>"
      ].join("");
    }).join("");
  }

  function renderGuide() {
    renderList("providesList", guide.provides);
    renderList("ownsList", guide.owns);
    renderList("pathList", guide.path);
  }

  function renderRoadmap() {
    const host = document.getElementById("roadmap");
    host.innerHTML = roadmap.map(function (item) {
      return [
        '<article class="roadmap-item">',
        '<span class="phase">' + escapeHtml(item[0]) + "</span>",
        "<div><h3>" + escapeHtml(item[1]) + "</h3><p>" + escapeHtml(item[2]) + "</p></div>",
        "</article>"
      ].join("");
    }).join("");
  }

  function renderList(id, items) {
    const host = document.getElementById(id);
    host.innerHTML = items.map(function (item) {
      return "<li>" + escapeHtml(item) + "</li>";
    }).join("");
  }

  function renderSourceLinks(sources) {
    return sources.slice(0, 2).map(function (source) {
      return '<a href="' + escapeAttribute(source.url) + '">' + escapeHtml(source.source_type || "source") + "</a>";
    }).join("");
  }

  function setupCanvas() {
    const canvas = document.getElementById("architectureCanvas");
    const context = canvas.getContext("2d");
    const labels = [
      ["OneRoster", "Roster"],
      ["CASE", "Standards"],
      ["QTI", "Assessment"],
      ["Caliper", "Events"],
      ["LTI", "Tools"],
      ["Open Badges", "Credentials"],
      ["SQL", "Relational"],
      ["JSON API", "Web"]
    ];
    let width = 0;
    let height = 0;
    let pixelRatio = 1;
    let nodes = [];
    let frame = 0;

    function resize() {
      const box = canvas.getBoundingClientRect();
      pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
      width = Math.max(320, Math.floor(box.width));
      height = Math.max(420, Math.floor(box.height));
      canvas.width = Math.floor(width * pixelRatio);
      canvas.height = Math.floor(height * pixelRatio);
      context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
      layoutNodes();
    }

    function layoutNodes() {
      const centerX = width * 0.67;
      const centerY = height * 0.47;
      const radiusX = Math.max(170, width * 0.22);
      const radiusY = Math.max(150, height * 0.22);
      nodes = labels.map(function (label, index) {
        const angle = -Math.PI / 2 + (Math.PI * 2 * index) / labels.length;
        return {
          name: label[0],
          role: label[1],
          x: centerX + Math.cos(angle) * radiusX,
          y: centerY + Math.sin(angle) * radiusY,
          color: ["#8fe1c8", "#74c8e8", "#f5c66d", "#f28d79", "#a99ae8", "#f0a8c0", "#ffffff", "#c8f2df"][index]
        };
      });
    }

    function draw() {
      frame += 0.008;
      context.clearRect(0, 0, width, height);
      drawBackground();
      drawConnections();
      drawCore();
      nodes.forEach(drawNode);
      requestAnimationFrame(draw);
    }

    function drawBackground() {
      const gradient = context.createLinearGradient(0, 0, width, height);
      gradient.addColorStop(0, "#0d211f");
      gradient.addColorStop(0.5, "#123530");
      gradient.addColorStop(1, "#203c47");
      context.fillStyle = gradient;
      context.fillRect(0, 0, width, height);

      context.strokeStyle = "rgba(255,255,255,0.055)";
      context.lineWidth = 1;
      const spacing = 44;
      for (let x = -spacing; x < width + spacing; x += spacing) {
        context.beginPath();
        context.moveTo(x + Math.sin(frame + x * 0.01) * 5, 0);
        context.lineTo(x - 70, height);
        context.stroke();
      }
      for (let y = 0; y < height; y += spacing) {
        context.beginPath();
        context.moveTo(0, y + Math.cos(frame + y * 0.012) * 4);
        context.lineTo(width, y - 40);
        context.stroke();
      }
    }

    function drawConnections() {
      const core = { x: width * 0.67, y: height * 0.47 };
      nodes.forEach(function (node, index) {
        context.beginPath();
        context.moveTo(core.x, core.y);
        context.lineTo(node.x, node.y);
        context.strokeStyle = "rgba(255,255,255,0.2)";
        context.lineWidth = 1.4;
        context.stroke();

        const t = (frame * 0.9 + index / nodes.length) % 1;
        const px = core.x + (node.x - core.x) * t;
        const py = core.y + (node.y - core.y) * t;
        context.beginPath();
        context.arc(px, py, 3.5, 0, Math.PI * 2);
        context.fillStyle = node.color;
        context.fill();
      });
    }

    function drawCore() {
      const x = width * 0.67;
      const y = height * 0.47;
      const pulse = 1 + Math.sin(frame * 5) * 0.035;
      context.save();
      context.translate(x, y);
      context.scale(pulse, pulse);
      roundRect(context, -108, -54, 216, 108, 12);
      context.fillStyle = "rgba(255,255,255,0.94)";
      context.fill();
      context.strokeStyle = "rgba(143,225,200,0.8)";
      context.lineWidth = 2;
      context.stroke();
      context.fillStyle = "#0f352f";
      context.font = "800 18px Inter, system-ui, sans-serif";
      context.textAlign = "center";
      context.fillText("Shared Dictionary", 0, -8);
      context.fillStyle = "#4f6861";
      context.font = "700 12px Inter, system-ui, sans-serif";
      context.fillText("SQL + JSON documentation", 0, 18);
      context.restore();
    }

    function drawNode(node) {
      const drift = Math.sin(frame * 4 + node.x * 0.01) * 4;
      context.save();
      context.translate(node.x, node.y + drift);
      roundRect(context, -66, -34, 132, 68, 10);
      context.fillStyle = "rgba(255,255,255,0.14)";
      context.fill();
      context.strokeStyle = "rgba(255,255,255,0.32)";
      context.stroke();
      context.beginPath();
      context.arc(-44, 0, 9, 0, Math.PI * 2);
      context.fillStyle = node.color;
      context.fill();
      context.fillStyle = "#ffffff";
      context.textAlign = "left";
      context.font = "800 13px Inter, system-ui, sans-serif";
      context.fillText(node.name, -28, -4);
      context.fillStyle = "rgba(255,255,255,0.68)";
      context.font = "700 10px Inter, system-ui, sans-serif";
      context.fillText(node.role, -28, 13);
      context.restore();
    }

    function roundRect(ctx, x, y, w, h, r) {
      const radius = Math.min(r, w / 2, h / 2);
      ctx.beginPath();
      ctx.moveTo(x + radius, y);
      ctx.arcTo(x + w, y, x + w, y + h, radius);
      ctx.arcTo(x + w, y + h, x, y + h, radius);
      ctx.arcTo(x, y + h, x, y, radius);
      ctx.arcTo(x, y, x + w, y, radius);
      ctx.closePath();
    }

    resize();
    window.addEventListener("resize", resize);
    requestAnimationFrame(draw);
  }

  function setText(id, value) {
    document.getElementById(id).textContent = value;
  }

  function unique(values) {
    return Array.from(new Set(values));
  }

  function titleCase(value) {
    return String(value)
      .replace(/_/g, " ")
      .replace(/\b\w/g, function (letter) {
        return letter.toUpperCase();
      });
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function escapeAttribute(value) {
    return escapeHtml(value).replace(/`/g, "&#96;");
  }
})();

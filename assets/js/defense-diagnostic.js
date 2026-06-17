/*
 * PoE2 Build Lab — defense diagnostic (Phase 6).
 * Maps death patterns to fixes; prefills per-build death_diagnostic from build JSON.
 */
(function () {
  "use strict";

  var DEFAULT_PATTERNS = [
    { pattern: "Boss one-shots you", cause: "Too little life/resists or missed dodge window", first_fix: "Add life/resists; learn telegraphs; improve spacing", gear_slot: "body_armour" },
    { pattern: "Packs overwhelm you", cause: "Weak clear or poor positioning", first_fix: "Improve AoE, kiting, or utility skill", gear_slot: "weapon" },
    { pattern: "Fights take too long", cause: "Damage scaling behind curve", first_fix: "Upgrade weapon/gem/supports", gear_slot: "weapon" },
    { pattern: "Always out of mana", cause: "Cost/recovery mismatch", first_fix: "Change supports or add recovery", gear_slot: "weapon" },
    { pattern: "Skill greys out after swap", cause: "Lost attribute requirement from gear", first_fix: "Restore attributes on amulet/rings", gear_slot: "amulet" },
  ];

  function $(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function renderTable(patterns) {
    var tbody = $("diag-results");
    if (!tbody) return;
    tbody.innerHTML = "";
    patterns.forEach(function (row) {
      var tr = document.createElement("tr");
      tr.innerHTML = "<td>" + esc(row.pattern) + "</td><td>" + esc(row.cause) + "</td>" +
        "<td>" + esc(row.first_fix) + "</td><td>" + esc((row.gear_slot || "").replace(/_/g, " ")) + "</td>";
      tbody.appendChild(tr);
    });
  }

  function filterPatterns() {
    var q = ($("diag-search") && $("diag-search").value || "").toLowerCase();
    var patterns = window.__diagPatterns || DEFAULT_PATTERNS;
    if (!q) {
      renderTable(patterns);
      return;
    }
    renderTable(patterns.filter(function (p) {
      return p.pattern.toLowerCase().indexOf(q) !== -1 ||
        p.cause.toLowerCase().indexOf(q) !== -1;
    }));
  }

  function initBuild(id) {
    fetch("../data/builds/" + id + ".json")
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (build) {
        if (!build) return;
        var banner = $("build-banner");
        if (banner) {
          banner.style.display = "block";
          banner.innerHTML = "<strong>Build-aware mode:</strong> " + esc(build.name) +
            " · <a href=\"../builds/" + esc(build.id) + ".html\">Open build card</a>";
        }
        var patterns = (build.defenses && build.defenses.death_diagnostic) || DEFAULT_PATTERNS;
        window.__diagPatterns = patterns;
        renderTable(patterns);
        var d = build.defenses || {};
        var targets = $("build-defense-targets");
        if (targets) {
          var html = "";
          if (d.campaign_targets) {
            html += "<h3>Campaign targets</h3><ul>" +
              d.campaign_targets.map(function (t) { return "<li>" + esc(t) + "</li>"; }).join("") + "</ul>";
          }
          if (d.early_maps_targets) {
            html += "<h3>Early maps targets</h3><ul>" +
              d.early_maps_targets.map(function (t) { return "<li>" + esc(t) + "</li>"; }).join("") + "</ul>";
          }
          if (d.map_mods_to_avoid && d.map_mods_to_avoid.length) {
            html += "<h3>Map mods to avoid</h3><ul>" +
              d.map_mods_to_avoid.map(function (t) { return "<li>" + esc(t) + "</li>"; }).join("") + "</ul>";
          }
          targets.innerHTML = html;
        }
      })
      .catch(function () {});
  }

  function init() {
    window.__diagPatterns = DEFAULT_PATTERNS;
    renderTable(DEFAULT_PATTERNS);
    var search = $("diag-search");
    if (search) search.addEventListener("input", filterPatterns);
    var params = new URLSearchParams(window.location.search);
    var id = params.get("build");
    if (id) initBuild(id);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

/*
 * PoE2 Build Lab — gear upgrade checker (Phase 4).
 * Loads build JSON from data/builds/?build=id and helps pick the next slot upgrade by stage.
 */
(function () {
  "use strict";

  var STAGES = [
    { key: "campaign", label: "Campaign" },
    { key: "early_maps", label: "Early maps" },
    { key: "red_maps", label: "Red maps / pinnacle" },
  ];

  function $(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function slotScore(slot, stageKey) {
    var targetKey = stageKey === "campaign" ? "campaign_target"
      : stageKey === "early_maps" ? "early_maps_target" : "red_maps_target";
    var t = slot[targetKey] || slot.campaign_target || "";
    return t ? 1 : 0;
  }

  function renderBuild(build) {
    var banner = $("build-banner");
    if (banner) {
      banner.style.display = "block";
      banner.innerHTML = "<strong>Prefilled from:</strong> " + esc(build.name) +
        " · <a href=\"../builds/" + esc(build.id) + ".html\">Open build card</a>";
    }

    var stage = $("upgrade-stage");
    var slotSel = $("upgrade-slot");
    var out = $("upgrade-output");
    if (!stage || !slotSel || !out) return;

    function refresh() {
      var stageKey = stage.value;
      var slotName = slotSel.value;
      var slot = build.gear_slots[slotName];
      if (!slot) {
        out.innerHTML = "<p class=\"muted\">No data for this slot.</p>";
        return;
      }
      var targetKey = stageKey === "campaign" ? "campaign_target"
        : stageKey === "early_maps" ? "early_maps_target" : "red_maps_target";
      var html = "<h3>" + esc(slotName.replace(/_/g, " ")) + " · " + esc(stage.options[stage.selectedIndex].text) + "</h3>";
      html += "<p><strong>Base:</strong> " + esc(slot.base) + "</p>";
      if (slot[targetKey]) {
        html += "<p><strong>Target for this stage:</strong> " + esc(slot[targetKey]) + "</p>";
      }
      if (slot.budget_compromise) {
        html += "<p class=\"muted\"><strong>Budget compromise:</strong> " + esc(slot.budget_compromise) + "</p>";
      }
      html += "<table class=\"gear\"><thead><tr><th>Tier</th><th>Affixes</th></tr></thead><tbody>";
      html += "<tr><th>Required</th><td>" + (slot.required_affixes || []).map(esc).join("; ") + "</td></tr>";
      html += "<tr><th>Good</th><td>" + (slot.good_affixes || []).map(esc).join("; ") + "</td></tr>";
      html += "<tr><th>Luxury</th><td>" + (slot.luxury_affixes || []).map(esc).join("; ") + "</td></tr>";
      html += "</tbody></table>";
      if (build.trade_handoff && build.trade_handoff.enabled) {
        var filt = (build.trade_handoff.filters || []).find(function (f) { return f.slot === slotName; });
        if (filt) {
          html += "<h3>Trade handoff</h3><p>" + esc(filt.filter_recipe || filt.required_stats.join(", ")) + "</p>";
          if (filt.trade_url) {
            html += "<p><a href=\"" + esc(filt.trade_url) + "\" rel=\"nofollow noopener\">Open official trade</a> " +
              "<span class=\"muted\">(filter manually — deep links may not prefill)</span></p>";
          }
        }
      }
      out.innerHTML = html;
    }

    slotSel.innerHTML = "";
    Object.keys(build.gear_slots).forEach(function (name) {
      var opt = document.createElement("option");
      opt.value = name;
      opt.textContent = name.replace(/_/g, " ");
      slotSel.appendChild(opt);
    });

    stage.onchange = refresh;
    slotSel.onchange = refresh;
    refresh();

    // Suggest next slot: lowest priority slot with campaign target not yet "done" — heuristic: first slot in list for stage
    var suggest = $("upgrade-suggest");
    if (suggest) {
      var ranked = Object.keys(build.gear_slots).map(function (name) {
        return { name: name, score: slotScore(build.gear_slots[name], stage.value) };
      }).filter(function (x) { return x.score > 0; });
      if (ranked.length) {
        suggest.innerHTML = "<strong>Suggested focus:</strong> start with <b>" +
          esc(ranked[0].name.replace(/_/g, " ")) + "</b> — " +
          esc(build.gear_slots[ranked[0].name].campaign_target || "see targets below") + ".";
      }
    }
  }

  function init() {
    var params = new URLSearchParams(window.location.search);
    var id = params.get("build");
    if (!id) return;
    fetch("../data/builds/" + id + ".json")
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) { if (data) renderBuild(data); })
      .catch(function () {});
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

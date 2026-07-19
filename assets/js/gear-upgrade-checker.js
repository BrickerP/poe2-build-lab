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

  function officialTradeUrl(value) {
    if (typeof value !== "string" || value !== value.trim() ||
        !/^https:\/\/www[.]pathofexile[.]com\//.test(value)) return "";
    try {
      var url = new URL(value);
      var validPath = url.pathname === "/trade2" ||
        url.pathname.indexOf("/trade2/search/poe2/") === 0;
      return url.protocol === "https:" && url.host === "www.pathofexile.com" &&
        !url.search && !url.hash && validPath ? value : "";
    } catch (error) {
      return "";
    }
  }

  function stageTarget(slot, stageKey) {
    var targetKey = stageKey === "campaign" ? "campaign_target"
      : stageKey === "early_maps" ? "early_maps_target" : "red_maps_target";
    return slot[targetKey] || "";
  }

  function isBuildData(build, id) {
    return build && build.id === id && typeof build.name === "string" &&
      build.gear_slots && typeof build.gear_slots === "object" &&
      !Array.isArray(build.gear_slots);
  }

  function renderDefaultState() {
    var slotSel = $("upgrade-slot");
    var suggest = $("upgrade-suggest");
    var out = $("upgrade-output");
    if (slotSel) slotSel.innerHTML = '<option value="">— choose a build above —</option>';
    if (suggest) suggest.textContent = "No build-specific suggestion is available.";
    if (out) {
      out.innerHTML = '<p class="muted">Open this tool from a build card or choose a build above to load slot targets.</p>';
    }
  }

  function renderLoadFailure(id) {
    var banner = $("build-banner");
    if (banner) {
      banner.className = "notice notice-warn notice-compact";
      banner.innerHTML = "<strong>Build data unavailable.</strong> Could not load build <code>" +
        esc(id) + "</code>. Choose a build above to continue.";
      banner.style.display = "block";
    }
    renderDefaultState();
  }

  function renderBuild(build) {
    var banner = $("build-banner");
    if (banner) {
      banner.className = "notice notice-compact";
      banner.style.display = "block";
      banner.innerHTML = "<strong>Prefilled from:</strong> " + esc(build.name) +
        " · <a href=\"../builds/" + esc(build.id) + ".html\">Open build card</a>";
    }

    var stage = $("upgrade-stage");
    var slotSel = $("upgrade-slot");
    var status = $("upgrade-suggest");
    var out = $("upgrade-output");
    if (!stage || !slotSel || !status || !out) return;

    function suggestionFor(stageKey) {
      var ranked = Object.keys(build.gear_slots).filter(function (name) {
        return Boolean(stageTarget(build.gear_slots[name], stageKey));
      });
      if (!ranked.length) return "";
      return "start with <b>" + esc(ranked[0].replace(/_/g, " ")) + "</b> — " +
        esc(stageTarget(build.gear_slots[ranked[0]], stageKey));
    }

    function refresh() {
      var stageKey = stage.value;
      var stageLabel = stage.options[stage.selectedIndex].text;
      var slotName = slotSel.value;
      var slot = build.gear_slots[slotName];
      if (!slot) {
        status.innerHTML = "<strong>" + esc(stageLabel) + ":</strong> no slot data is available.";
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
          var tradeUrl = officialTradeUrl(filt.trade_url);
          if (tradeUrl) {
            html += "<p><a href=\"" + esc(tradeUrl) + "\" rel=\"nofollow noopener\">Open official trade</a> " +
              "<span class=\"muted\">(filter manually — deep links may not prefill)</span></p>";
          } else {
            html += "<p class=\"muted\"><strong>Official trade link unavailable.</strong> " +
              "Use the filter recipe manually.</p>";
          }
        }
      }
      out.innerHTML = html;

      var suggestion = suggestionFor(stageKey);
      var selectedTarget = stageTarget(slot, stageKey) || "no authored target";
      status.innerHTML = "<strong>" + esc(stageLabel) + ":</strong> " +
        (suggestion ? "suggested focus is to " + suggestion + ". " : "") +
        "Selected <b>" + esc(slotName.replace(/_/g, " ")) + "</b>: " +
        esc(selectedTarget) + ".";
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
  }

  function init() {
    var params = new URLSearchParams(window.location.search);
    var id = params.get("build");
    if (!id) {
      renderDefaultState();
      return;
    }
    if (!/^[a-z0-9-]+$/.test(id)) {
      renderLoadFailure(id);
      return;
    }
    fetch("../data/builds/" + id + ".json")
      .then(function (r) {
        if (!r.ok) throw new Error("build request failed");
        return r.json();
      })
      .then(function (data) {
        if (!isBuildData(data, id)) throw new Error("invalid build data");
        renderBuild(data);
      })
      .catch(function () { renderLoadFailure(id); });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

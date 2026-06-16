/*
 * PoE2 Build Lab — attribute, Spirit, and gear-swap calculator.
 *
 * Vanilla JS, no backend. Reads an optional ?build=<id> query param and prefills
 * from data/builds/<id>.json (the same data object the build pages render from),
 * including the differentiators: spirit_budget and gear_swap_warnings.
 *
 * This is a planning aid. Exact gem/base attribute requirements need a verified
 * data source; until then the numeric inputs are user-supplied.
 */
(function () {
  "use strict";

  var ATTRS = [
    { key: "str", label: "Strength" },
    { key: "dex", label: "Dexterity" },
    { key: "int", label: "Intelligence" }
  ];
  // Keywords that indicate a gear slot can supply a given attribute.
  var ATTR_KEYWORDS = {
    str: ["strength", "str", "attribute"],
    dex: ["dexterity", "dex", "attribute"],
    int: ["intelligence", "int", "attribute"]
  };

  var currentBuild = null;

  function $(id) { return document.getElementById(id); }
  function num(id) {
    var el = $(id);
    if (!el) return 0;
    var v = parseInt(el.value, 10);
    return isNaN(v) ? 0 : v;
  }
  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function slotsSupplying(attrKey) {
    if (!currentBuild || !currentBuild.gear_slots) return [];
    var kws = ATTR_KEYWORDS[attrKey];
    var hits = [];
    Object.keys(currentBuild.gear_slots).forEach(function (slot) {
      var prio = (currentBuild.gear_slots[slot].priority || []).join(" ").toLowerCase();
      if (kws.some(function (kw) { return prio.indexOf(kw) !== -1; })) {
        hits.push(slot.replace(/_/g, " "));
      }
    });
    return hits;
  }

  /* ----- Attributes ----- */
  function computeAttributes() {
    var out = $("attr-results");
    out.innerHTML = "";
    var anyDeficit = false;
    ATTRS.forEach(function (a) {
      var required = num("req-" + a.key);
      var current = num("cur-" + a.key);
      var gear = num("gear-" + a.key);
      var effective = current + gear;
      var deficit = required - effective;
      var row = el("tr");
      var status, cls;
      if (deficit > 0) {
        anyDeficit = true;
        var fixers = slotsSupplying(a.key);
        var fixHtml = fixers.length
          ? ' <span class="muted">Slots that can add ' + a.label + ": " + esc(fixers.join(", ")) + ".</span>"
          : "";
        status = "Short by <b>" + deficit + "</b>" + fixHtml;
        cls = "bad";
      } else {
        status = "Met (" + (deficit === 0 ? "exactly" : (-deficit) + " to spare") + ")";
        cls = "ok";
      }
      row.innerHTML =
        "<th>" + a.label + "</th>" +
        "<td>" + required + "</td>" +
        "<td>" + effective + " <span class='muted'>(" + current + " + " + gear + ")</span></td>" +
        "<td class='res-" + cls + "'>" + status + "</td>";
      out.appendChild(row);
    });
    $("attr-summary").textContent = anyDeficit
      ? "You have at least one attribute deficit — see which gear slots can fix it below."
      : "All entered attribute requirements are met.";
    $("attr-summary").className = "calc-summary " + (anyDeficit ? "res-bad" : "res-ok");
  }

  /* ----- Spirit ----- */
  function computeSpirit() {
    var capacity = num("spirit-capacity");
    var reserved = num("spirit-reserved");
    var deficit = reserved - capacity;
    var box = $("spirit-result");
    if (deficit > 0) {
      box.className = "calc-summary res-bad";
      box.textContent = "Spirit over-reserved by " + deficit + ". You cannot sustain all reservations — drop a reservation or add Spirit.";
    } else {
      box.className = "calc-summary res-ok";
      box.textContent = "Spirit OK: " + reserved + " reserved of " + capacity + " (" + (capacity - reserved) + " free).";
    }
    // Itemized sources from the build, if any.
    var srcBox = $("spirit-sources");
    srcBox.innerHTML = "";
    if (currentBuild && currentBuild.spirit_budget && (currentBuild.spirit_budget.sources || []).length) {
      var ul = el("ul");
      currentBuild.spirit_budget.sources.forEach(function (s) {
        ul.appendChild(el("li", null, esc(s.name) + ": " + esc(String(s.amount))));
      });
      srcBox.appendChild(el("p", "muted", "Reservation sources from this build:"));
      srcBox.appendChild(ul);
    }
  }

  /* ----- Gear swap ----- */
  function populateSwapSlots() {
    var sel = $("swap-slot");
    sel.innerHTML = '<option value="">— choose a slot —</option>';
    var slots = currentBuild && currentBuild.gear_slots
      ? Object.keys(currentBuild.gear_slots)
      : ["weapon", "body_armour", "helmet", "gloves", "boots", "belt", "amulet", "ring_1", "ring_2"];
    slots.forEach(function (s) {
      var o = el("option");
      o.value = s;
      o.textContent = s.replace(/_/g, " ");
      sel.appendChild(o);
    });
  }

  function computeGearSwap() {
    var slot = $("swap-slot").value;
    var out = $("swap-result");
    out.innerHTML = "";
    if (!slot) {
      out.appendChild(el("p", "muted", "Choose the slot you are thinking of swapping."));
      return;
    }

    // 1. Build-authored swap warnings for this slot (the differentiator).
    var warnings = (currentBuild && currentBuild.gear_swap_warnings || []).filter(function (w) {
      return w.slot === slot;
    });
    if (warnings.length) {
      warnings.forEach(function (w) {
        var breaks = (w.breaks || []).length ? "<br><span class='muted'>Breaks: " + esc(w.breaks.join(", ")) + "</span>" : "";
        var removed = (w.removed_stats || []).length ? "<br><span class='muted'>Watch for: " + esc(w.removed_stats.join(", ")) + "</span>" : "";
        out.appendChild(el("div", "notice notice-bad", "<strong>" + esc(slot.replace(/_/g, " ")) + ":</strong> " + esc(w.message) + breaks + removed));
      });
    } else if (currentBuild) {
      out.appendChild(el("div", "notice", "No build-authored breakage is recorded for this slot. Still verify attributes and Spirit below before swapping."));
    } else {
      out.appendChild(el("div", "notice notice-warn", "Load a build (open this tool from a build card) to see build-specific swap warnings."));
    }

    // 2. Numeric re-check: removing this slot's attributes/Spirit.
    var lostStr = num("swap-str"), lostDex = num("swap-dex"), lostInt = num("swap-int"), lostSpirit = num("swap-spirit");
    var lines = [];
    ATTRS.forEach(function (a) {
      var lost = a.key === "str" ? lostStr : a.key === "dex" ? lostDex : lostInt;
      if (lost <= 0) return;
      var required = num("req-" + a.key);
      var effectiveAfter = num("cur-" + a.key) + num("gear-" + a.key) - lost;
      var deficitAfter = required - effectiveAfter;
      if (deficitAfter > 0) {
        lines.push("Removing " + lost + " " + a.label + " drops you " + deficitAfter + " below your " + a.label + " requirement — a gated skill or item base may stop working.");
      }
    });
    if (lostSpirit > 0) {
      var capAfter = num("spirit-capacity") - lostSpirit;
      var reserved = num("spirit-reserved");
      if (reserved > capAfter) {
        lines.push("Removing " + lostSpirit + " Spirit leaves " + capAfter + " capacity for " + reserved + " reserved — a reservation (aura/minion/companion) will drop.");
      }
    }
    if (lines.length) {
      var ul = el("ul");
      lines.forEach(function (l) { ul.appendChild(el("li", null, esc(l))); });
      var box = el("div", "notice notice-bad");
      box.appendChild(el("strong", null, "Simulated swap breaks something:"));
      box.appendChild(ul);
      out.appendChild(box);
    } else if (lostStr + lostDex + lostInt + lostSpirit > 0) {
      out.appendChild(el("div", "notice", "<strong>Simulated swap looks safe</strong> for the attributes/Spirit you entered (no requirement goes negative). Verify in game."));
    }
  }

  /* ----- Prefill from build JSON ----- */
  function setVal(id, v) { var e = $(id); if (e && (v || v === 0)) e.value = v; }

  function prefill(build) {
    currentBuild = build;
    var banner = $("build-banner");
    var asc = build.ascendancy && build.ascendancy !== "TBD" ? " · " + build.ascendancy : "";
    banner.innerHTML = "Prefilled from <b>" + esc(build.name) + "</b> (" + esc(build.class || "") + esc(asc) + "). " +
      "Exact gem/base attribute requirements are pending verified data, so requirement fields start at 0 — enter the requirement you want to meet.";
    banner.style.display = "block";

    var req = (build.attributes && build.attributes.required) || {};
    var planned = (build.attributes && build.attributes.planned) || {};
    ATTRS.forEach(function (a) {
      setVal("req-" + a.key, req[a.key] || 0);
      setVal("cur-" + a.key, planned[a.key] || 0);
    });
    if (build.spirit_budget) {
      setVal("spirit-reserved", build.spirit_budget.required || 0);
      setVal("spirit-capacity", build.spirit_budget.planned || 0);
    }
    populateSwapSlots();
    recalcAll();
  }

  function recalcAll() {
    computeAttributes();
    computeSpirit();
    computeGearSwap();
  }

  function loadBuildFromQuery() {
    var params = new URLSearchParams(window.location.search);
    var id = params.get("build");
    if (!id || !/^[a-z0-9-]+$/.test(id)) {
      populateSwapSlots();
      recalcAll();
      return;
    }
    fetch("../data/builds/" + id + ".json")
      .then(function (r) { if (!r.ok) throw new Error("not found"); return r.json(); })
      .then(prefill)
      .catch(function () {
        var banner = $("build-banner");
        banner.innerHTML = "Could not load build <code>" + esc(id) + "</code>. Enter values manually below.";
        banner.style.display = "block";
        populateSwapSlots();
        recalcAll();
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("#attr-calc input, #spirit-calc input").forEach(function (i) {
      i.addEventListener("input", recalcAll);
    });
    $("swap-slot").addEventListener("change", computeGearSwap);
    document.querySelectorAll("#swap-calc input").forEach(function (i) {
      i.addEventListener("input", computeGearSwap);
    });
    loadBuildFromQuery();
  });
})();

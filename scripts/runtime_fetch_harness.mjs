import vm from "node:vm";

const base = process.argv[2];
if (!base) throw new Error("usage: node runtime_fetch_harness.mjs <site-url>");

const nativeFetch = globalThis.fetch;
const adDomains = [
  "adservice.google.com", "doubleclick.net", "google-analytics.com",
  "googleadservices.com", "googlesyndication.com", "googletagmanager.com",
  "googletagservices.com"
];

class Element {
  constructor(tag = "div") {
    this.tagName = tag.toUpperCase();
    this.children = [];
    this.style = {};
    this.options = [];
    this.selectedIndex = 0;
    this.value = "";
    this._innerHTML = "";
    this.textContent = "";
  }
  set innerHTML(value) { this._innerHTML = String(value); this.children = []; }
  get innerHTML() { return this._innerHTML; }
  appendChild(child) {
    this.children.push(child);
    if (this.tagName === "SELECT") {
      this.options.push(child);
      if (this.options.length === 1) this.value = child.value;
    }
    return child;
  }
  addEventListener() {}
}

function documentFixture(ids, selectFixtures = {}) {
  const elements = new Map(ids.map((id) => [id, new Element()]));
  for (const [id, fixture] of Object.entries(selectFixtures)) {
    const element = new Element("select");
    Object.assign(element, fixture);
    elements.set(id, element);
  }
  return {
    readyState: "complete",
    getElementById(id) { return elements.get(id) || null; },
    createElement(tag) { return new Element(tag); },
    querySelectorAll() { return []; },
    addEventListener(event, callback) { if (event === "DOMContentLoaded") callback(); },
    elements
  };
}

const cases = [
  {
    page: "tools/attribute-checker.html?build=starter-elemental-caster",
    script: "assets/js/attribute-calculator.js",
    ids: ["build-banner", "attr-results", "attr-summary", "spirit-result", "spirit-sources",
      "swap-result", "attr-calc", "spirit-calc", "swap-calc", "req-str", "req-dex", "req-int",
      "cur-str", "cur-dex", "cur-int", "gear-str", "gear-dex", "gear-int", "spirit-capacity",
      "spirit-reserved", "swap-str", "swap-dex", "swap-int", "swap-spirit"],
    selects: {"swap-slot": {}},
    marker: "Prefilled from <b>"
  },
  {
    page: "tools/beginner-build-checklist.html?build=starter-minion-witch",
    script: "assets/js/defense-diagnostic.js",
    ids: ["build-banner", "diag-results", "diag-search", "build-defense-targets"],
    selects: {},
    marker: "Build-aware mode:"
  },
  {
    page: "tools/gear-upgrade-checker.html?build=starter-elemental-caster",
    script: "assets/js/gear-upgrade-checker.js",
    ids: ["build-banner", "upgrade-output", "upgrade-suggest"],
    selects: {
      "upgrade-stage": {
        value: "campaign",
        options: [{text: "Campaign"}, {text: "Early maps"}, {text: "Red maps / pinnacle"}],
        selectedIndex: 0
      },
      "upgrade-slot": {}
    },
    marker: "Prefilled from:"
  }
];

for (const testCase of cases) {
  const pageUrl = new URL(testCase.page, base);
  const requests = [];
  globalThis.window = globalThis;
  globalThis.location = {search: pageUrl.search};
  globalThis.document = documentFixture(testCase.ids, testCase.selects);
  globalThis.fetch = (input, init) => {
    const url = new URL(input, pageUrl);
    requests.push(url.href);
    return nativeFetch(url, init);
  };

  const pageResponse = await globalThis.fetch(pageUrl);
  if (!pageResponse.ok) throw new Error(`${testCase.page}: HTTP ${pageResponse.status}`);
  const pageHtml = await pageResponse.text();
  if (!pageHtml.includes(testCase.script.split("/").at(-1))) {
    throw new Error(`${testCase.page}: expected packaged script is not referenced`);
  }
  const scriptResponse = await globalThis.fetch(new URL(testCase.script, base));
  if (!scriptResponse.ok) throw new Error(`${testCase.script}: HTTP ${scriptResponse.status}`);
  vm.runInThisContext(await scriptResponse.text(), {filename: testCase.script});

  const banner = document.getElementById("build-banner");
  for (let attempt = 0; attempt < 100 && !banner.innerHTML.includes(testCase.marker); attempt++) {
    await new Promise((resolve) => setTimeout(resolve, 10));
  }
  if (!banner.innerHTML.includes(testCase.marker) || banner.style.display !== "block") {
    throw new Error(`${testCase.page}: build-aware UI did not render; banner=${banner.innerHTML}`);
  }
  const expectedData = `/data/builds/${new URLSearchParams(pageUrl.search).get("build")}.json`;
  if (!requests.some((request) => new URL(request).pathname.endsWith(expectedData))) {
    throw new Error(`${testCase.page}: runtime build JSON was not fetched over HTTP`);
  }
  if (testCase.script.endsWith("gear-upgrade-checker.js")) {
    const stage = document.getElementById("upgrade-stage");
    const suggestion = document.getElementById("upgrade-suggest");
    const output = document.getElementById("upgrade-output");
    if (!suggestion.innerHTML.includes("Campaign:") ||
        !suggestion.innerHTML.includes("Any wand with spell/elemental damage") ||
        !suggestion.innerHTML.includes("Selected <b>weapon</b>")) {
      throw new Error(`gear suggestion did not use campaign target: ${suggestion.innerHTML}`);
    }
    stage.value = "early_maps";
    stage.selectedIndex = 1;
    stage.onchange();
    if (!suggestion.innerHTML.includes("Early maps:") ||
        !suggestion.innerHTML.includes("+1 levels with cast speed if affordable")) {
      throw new Error(`gear suggestion did not update for early maps: ${suggestion.innerHTML}`);
    }
    if (!output.innerHTML.includes("Target for this stage:</strong> +1 levels with cast speed if affordable")) {
      throw new Error(`gear target did not update for early maps: ${output.innerHTML}`);
    }
    if (!output.innerHTML.includes('href="https://www.pathofexile.com/trade2"')) {
      throw new Error(`official trade landing URL did not render: ${output.innerHTML}`);
    }
    const initialStatus = suggestion.innerHTML;
    const slot = document.getElementById("upgrade-slot");
    slot.value = "body_armour";
    slot.onchange();
    if (suggestion.innerHTML === initialStatus ||
        !suggestion.innerHTML.includes("Selected <b>body armour</b>: Fill resistance gaps before luxury ES")) {
      throw new Error(`gear status did not update for selected slot: ${suggestion.innerHTML}`);
    }
  }
  for (const request of requests) {
    const parsed = new URL(request);
    if (parsed.origin !== new URL(base).origin) throw new Error(`external HTTP request: ${request}`);
    if (adDomains.some((domain) => parsed.hostname === domain || parsed.hostname.endsWith(`.${domain}`))) {
      throw new Error(`advertising HTTP request: ${request}`);
    }
  }
  console.log(`PASS ${testCase.page}: fetched runtime JSON and rendered build-aware state`);
}

const navCases = [
  {page: "index.html", href: "index.html", current: true},
  {page: "builds/index.html", href: "../builds/index.html", current: true},
  {page: "tools/gear-upgrade-checker.html", href: "../tools/gear-upgrade-checker.html", current: true},
  {page: "builds/starter-elemental-caster.html", href: "../builds/index.html", current: false},
  {page: "guides/beginner-guide.html", href: "../guides/index.html", current: false}
];

for (const testCase of navCases) {
  const response = await nativeFetch(new URL(testCase.page, base));
  if (!response.ok) throw new Error(`${testCase.page}: HTTP ${response.status}`);
  const html = await response.text();
  const nav = html.match(/<nav>([\s\S]*?)<\/nav>/);
  if (!nav) throw new Error(`${testCase.page}: navigation is missing`);
  const currentCount = (nav[1].match(/aria-current="page"/g) || []).length;
  const escapedHref = testCase.href.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const link = nav[1].match(new RegExp(`<a class="([^"]*)" href="${escapedHref}"([^>]*)>`));
  if (!link || !link[1].split(/\s+/).includes("active")) {
    throw new Error(`${testCase.page}: expected ${testCase.href} to keep the visual active state`);
  }
  const hasCurrent = link[2].includes('aria-current="page"');
  if (hasCurrent !== testCase.current || currentCount !== (testCase.current ? 1 : 0)) {
    throw new Error(`${testCase.page}: aria-current must identify only an exact nav destination; count=${currentCount}`);
  }
  console.log(`PASS ${testCase.page}: visual section state and exact-page aria-current are distinct`);
}

const gearResponse = await nativeFetch(new URL("tools/gear-upgrade-checker.html", base));
if (!gearResponse.ok) throw new Error(`tools/gear-upgrade-checker.html: HTTP ${gearResponse.status}`);
const gearHtml = await gearResponse.text();
if (!/id="upgrade-suggest"[^>]*role="status"[^>]*aria-live="polite"[^>]*aria-atomic="true"/.test(gearHtml)) {
  throw new Error("gear status must be one polite, atomic live region");
}
if (/id="upgrade-output"[^>]*(?:role="status"|aria-live=)/.test(gearHtml)) {
  throw new Error("gear output must not duplicate the consolidated live status");
}

const gearScriptResponse = await nativeFetch(new URL("assets/js/gear-upgrade-checker.js", base));
if (!gearScriptResponse.ok) throw new Error(`assets/js/gear-upgrade-checker.js: HTTP ${gearScriptResponse.status}`);
const gearScriptSource = await gearScriptResponse.text();
const buildResponse = await nativeFetch(new URL("data/builds/starter-elemental-caster.json", base));
if (!buildResponse.ok) throw new Error(`starter-elemental-caster.json: HTTP ${buildResponse.status}`);
const baseGearBuild = await buildResponse.json();
const hostileTradeUrls = [
  ["javascript", "javascript:alert(1)"],
  ["data", "data:text/html,unsafe"],
  ["scheme-relative", "//www.pathofexile.com/trade2"],
  ["off-domain", "https://example.com/trade2"],
  ["wrong-path", "https://www.pathofexile.com/forum"],
  ["missing", null]
];

for (const [label, tradeUrl] of hostileTradeUrls) {
  const build = JSON.parse(JSON.stringify(baseGearBuild));
  if (tradeUrl === null) delete build.trade_handoff.filters[0].trade_url;
  else build.trade_handoff.filters[0].trade_url = tradeUrl;
  const pageUrl = new URL("tools/gear-upgrade-checker.html?build=starter-elemental-caster", base);
  globalThis.window = globalThis;
  globalThis.location = {search: pageUrl.search};
  globalThis.document = documentFixture(
    ["build-banner", "upgrade-output", "upgrade-suggest"],
    {
      "upgrade-stage": {
        value: "campaign",
        options: [{text: "Campaign"}, {text: "Early maps"}, {text: "Red maps / pinnacle"}],
        selectedIndex: 0
      },
      "upgrade-slot": {}
    }
  );
  globalThis.fetch = () => Promise.resolve(new Response(JSON.stringify(build), {status: 200}));
  vm.runInThisContext(gearScriptSource, {filename: `gear-upgrade-checker.js (${label} trade URL)`});
  const banner = document.getElementById("build-banner");
  for (let attempt = 0; attempt < 100 && !banner.innerHTML.includes("Prefilled from:"); attempt++) {
    await new Promise((resolve) => setTimeout(resolve, 10));
  }
  const output = document.getElementById("upgrade-output").innerHTML;
  if (output.includes("<a ") || !output.includes("Official trade link unavailable")) {
    throw new Error(`gear ${label} trade URL did not fail closed: ${output}`);
  }
  console.log(`PASS gear ${label} trade URL: explicit non-link fallback`);
}

const failureTools = [
  {
    page: "tools/beginner-build-checklist.html",
    script: "assets/js/defense-diagnostic.js",
    ids: ["build-banner", "diag-results", "diag-search", "build-defense-targets"],
    selects: {},
    fallbackReady() { return document.getElementById("diag-results").children.length > 0; }
  },
  {
    page: "tools/gear-upgrade-checker.html",
    script: "assets/js/gear-upgrade-checker.js",
    ids: ["build-banner", "upgrade-output", "upgrade-suggest"],
    selects: {
      "upgrade-stage": {
        value: "campaign",
        options: [{text: "Campaign"}, {text: "Early maps"}, {text: "Red maps / pinnacle"}],
        selectedIndex: 0
      },
      "upgrade-slot": {}
    },
    fallbackReady() { return document.getElementById("upgrade-output").innerHTML.includes("build card"); }
  }
];

const failures = [
  {name: "404", id: "missing-build", respond: (url) => nativeFetch(url)},
  {name: "invalid JSON", id: "invalid-json", respond: () => Promise.resolve(new Response("{", {status: 200}))},
  {name: "rejected fetch", id: "rejected-fetch", respond: () => Promise.reject(new Error("offline"))},
  {name: "unsafe id", id: "../unsafe", respond: () => { throw new Error("unsafe build id was fetched"); }}
];

for (const tool of failureTools) {
  const pageResponse = await nativeFetch(new URL(tool.page, base));
  if (!pageResponse.ok) throw new Error(`${tool.page}: HTTP ${pageResponse.status}`);
  const pageHtml = await pageResponse.text();
  if (!/id="build-banner"[^>]*role="status"[^>]*aria-live="polite"/.test(pageHtml)) {
    throw new Error(`${tool.page}: failure banner is not a polite status region`);
  }
  const scriptResponse = await nativeFetch(new URL(tool.script, base));
  if (!scriptResponse.ok) throw new Error(`${tool.script}: HTTP ${scriptResponse.status}`);
  const scriptSource = await scriptResponse.text();

  for (const failure of failures) {
    const pageUrl = new URL(`${tool.page}?build=${encodeURIComponent(failure.id)}`, base);
    const requests = [];
    globalThis.window = globalThis;
    globalThis.location = {search: pageUrl.search};
    globalThis.document = documentFixture(tool.ids, tool.selects);
    globalThis.fetch = (input) => {
      const url = new URL(input, pageUrl);
      requests.push(url.href);
      return failure.respond(url);
    };
    vm.runInThisContext(scriptSource, {filename: `${tool.script} (${failure.name})`});

    const banner = document.getElementById("build-banner");
    for (let attempt = 0; attempt < 100 && !banner.innerHTML.includes("Could not load build"); attempt++) {
      await new Promise((resolve) => setTimeout(resolve, 10));
    }
    if (!banner.innerHTML.includes("Could not load build") || banner.style.display !== "block") {
      throw new Error(`${tool.page} ${failure.name}: explicit failure state missing; banner=${banner.innerHTML}`);
    }
    if (!tool.fallbackReady()) {
      throw new Error(`${tool.page} ${failure.name}: manual/default fallback is not usable`);
    }
    const expectedRequests = failure.name === "unsafe id" ? 0 : 1;
    if (requests.length !== expectedRequests) {
      throw new Error(`${tool.page} ${failure.name}: expected ${expectedRequests} build requests, got ${requests.length}`);
    }
    console.log(`PASS ${tool.page} ${failure.name}: explicit failure with usable fallback`);
  }
}

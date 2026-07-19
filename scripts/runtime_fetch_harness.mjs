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
      "upgrade-stage": {value: "campaign", options: [{text: "Campaign"}], selectedIndex: 0},
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
  for (const request of requests) {
    const parsed = new URL(request);
    if (parsed.origin !== new URL(base).origin) throw new Error(`external HTTP request: ${request}`);
    if (adDomains.some((domain) => parsed.hostname === domain || parsed.hostname.endsWith(`.${domain}`))) {
      throw new Error(`advertising HTTP request: ${request}`);
    }
  }
  console.log(`PASS ${testCase.page}: fetched runtime JSON and rendered build-aware state`);
}

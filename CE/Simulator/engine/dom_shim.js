// dom_shim.js — a do-nothing browser for running the settlement board's script headless.
// Every element is a "ghost": any property reads as another ghost, any call returns a ghost, it iterates as empty and
// prints as "". Lists (querySelectorAll, children) are empty arrays. Nothing is drawn; only game state matters.
"use strict";
function ghost() {
  const store = {};
  const fn = function () { return ghost(); };
  return new Proxy(fn, {
    get(t, k) {
      if (k in store) return store[k];
      if (k === Symbol.iterator) return function* () {};
      if (k === Symbol.toPrimitive) return () => "";
      if (k === "then") return undefined;                       // never thenable
      if (k === "toString" || k === "valueOf") return () => "";
      if (k === "length" || k === "scrollTop" || k === "scrollLeft" || k === "offsetWidth" || k === "offsetHeight" || k === "clientWidth" || k === "clientHeight") return 0;
      if (k === "value" || k === "textContent" || k === "innerHTML" || k === "innerText" || k === "className" || k === "id") return "";
      if (k === "checked" || k === "open" || k === "hidden" || k === "disabled") return false;
      if (k === "querySelectorAll" || k === "getElementsByClassName" || k === "getElementsByTagName") return () => [];
      if (k === "children" || k === "childNodes" || k === "options" || k === "files") return [];
      if (k === "closest" || k === "querySelector") return () => ghost();
      if (k === "parentElement" || k === "parentNode") return ghost();
      if (k === "matches" || k === "contains" || k === "hasAttribute") return () => false;
      if (k === "getAttribute") return () => null;
      if (k === "getBoundingClientRect") return () => ({ x: 0, y: 0, width: 0, height: 0, top: 0, left: 0, right: 0, bottom: 0 });
      if (k === "classList") return { add() {}, remove() {}, toggle() {}, contains() { return false; } };
      const g = ghost(); store[k] = g; return g;
    },
    set(t, k, v) { store[k] = v; return true; },
    apply() { return ghost(); },
    construct() { return ghost(); },
    has() { return true; },
  });
}
function makeDocument() {
  const byId = {};
  const doc = {
    getElementById(id) { return byId[id] || (byId[id] = ghost()); },
    querySelector() { return ghost(); },
    querySelectorAll() { return []; },
    createElement() { return ghost(); },
    createElementNS() { return ghost(); },
    createTextNode() { return ghost(); },
    addEventListener() {}, removeEventListener() {},
    body: ghost(), documentElement: ghost(), head: ghost(),
    hidden: false, visibilityState: "visible", title: "",
  };
  return doc;
}
function makeStorage() {
  const m = new Map();
  return { getItem: k => (m.has(k) ? m.get(k) : null), setItem: (k, v) => m.set(k, String(v)), removeItem: k => m.delete(k), clear: () => m.clear(), key: i => [...m.keys()][i] ?? null, get length() { return m.size; } };
}
// the sandbox globals the board's script expects
function makeWindowGlobals(rng) {
  const doc = makeDocument();
  const g = {
    document: doc, localStorage: makeStorage(), sessionStorage: makeStorage(),
    navigator: { userAgent: "renown-sim", clipboard: { writeText() { return Promise.resolve(); } } },
    location: { href: "http://sim/", search: "", hash: "", host: "sim", hostname: "sim", origin: "http://sim", pathname: "/", reload() {} },
    history: { replaceState() {}, pushState() {} },
    alert() {}, confirm() { return true; }, prompt() { return ""; },
    fetch() { return Promise.reject(new Error("offline")); },     // no server: the board runs pass-and-play
    setTimeout() { return 0; }, clearTimeout() {}, setInterval() { return 0; }, clearInterval() {},
    requestAnimationFrame() { return 0; }, cancelAnimationFrame() {},
    matchMedia() { return { matches: false, addEventListener() {}, addListener() {} }; },
    getComputedStyle() { return ghost(); },
    addEventListener() {}, removeEventListener() {},
    innerWidth: 1600, innerHeight: 1000, devicePixelRatio: 1,
    Blob: function () {}, URL: { createObjectURL() { return ""; }, revokeObjectURL() {} },
    FileReader: function () {}, Image: function () { return ghost(); }, Audio: function () { return ghost(); },
    ResizeObserver: function () { return { observe() {}, disconnect() {} }; },
    IntersectionObserver: function () { return { observe() {}, disconnect() {} }; },
    MutationObserver: function () { return { observe() {}, disconnect() {} }; },
    performance: { now: () => Date.now() },
    console,
  };
  if (rng) g.Math = Object.assign(Object.create(Math), { random: rng });
  return g;
}
module.exports = { ghost, makeWindowGlobals };

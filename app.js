/* ============================================================
   Latihan Bahasa Rusia — app.js

   Data dimuat dari webdata.js (global RUS_DATA), bukan lewat fetch(),
   sehingga aplikasi jalan di GitHub Pages maupun saat index.html dibuka
   langsung dari berkas (file://).

   Penjadwalan memakai lima kotak Leitner, sama seperti quiz.py. Progres
   disimpan di localStorage peramban dan tidak dikirim ke mana pun.
   ============================================================ */

"use strict";

/* ---------------------------------------------------- penyimpanan ---- */

const LS = { prog: "rus.progress.v1", prefs: "rus.prefs.v1", theme: "rus.theme" };

function lsGet(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch { return fallback; }
}
function lsSet(key, val) {
  try { localStorage.setItem(key, JSON.stringify(val)); } catch { /* mode privat */ }
}

/* Jeda ulangan per kotak, dalam hari. Sama dengan INTERVALS di
   rusdrill/leitner.py; ubah keduanya bila ingin jadwal lain. */
const BOX_DAYS = { 1: 0, 2: 1, 3: 3, 4: 7, 5: 16 };
const MAX_BOX = 5;

const progress = lsGet(LS.prog, { cards: {} });
if (!progress.cards) progress.cards = {};

const prefs = Object.assign(
  { translit: false, lafal: true, tekanan: false, arah: false, yo: false, due: false, hide: false },
  lsGet(LS.prefs, {})
);

function todayISO() {
  const d = new Date();
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}
function addDays(iso, n) {
  const d = new Date(iso + "T00:00:00");
  d.setDate(d.getDate() + n);
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}
function stateOf(id) { return progress.cards[id] || null; }
function boxOf(id) { const s = stateOf(id); return s ? s.box : 0; }
function isDue(id) {
  const s = stateOf(id);
  if (!s) return true;                 // kartu baru selalu dianggap jatuh tempo
  return s.due <= todayISO();
}
function grade(id, ok) {
  const s = stateOf(id) || { box: 1, due: todayISO(), seen: 0, right: 0 };
  s.seen += 1;
  if (ok) { s.right += 1; s.box = Math.min(s.box + 1, MAX_BOX); }
  else { s.box = 1; }
  s.due = addDays(todayISO(), BOX_DAYS[s.box]);
  progress.cards[id] = s;
  lsSet(LS.prog, progress);
}

/* ---------------------------------------------------------- utilitas ---- */

const $ = (sel) => document.querySelector(sel);
const esc = (s) => String(s)
  .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;");

function ru(text, size) {
  return `<div class="ru ${size || "ru-lg"}" lang="ru">${esc(text)}</div>`;
}
function tr(text) {
  return prefs.translit && text ? `<div class="tr">${esc(text)}</div>` : "";
}
function lafal(text) {
  return prefs.lafal && text ? `<div class="lafal">${esc(text)}</div>` : "";
}
/* Sisi DEPAN kartu kosakata: tanda tekanan boleh disembunyikan untuk melatih
   membaca teks Rusia yang sebenarnya. */
function frontRu(x) {
  return prefs.tekanan ? x.bare : x.ru;
}

/* ----------------------------------------------------- pembuat kartu ---- */

const D = typeof RUS_DATA !== "undefined" ? RUS_DATA : null;

const MODES = {
  alfabet: {
    label: "Alfabet",
    toggles: [],
    items: () => D.alfabet,
    search: (x) => x.kind === "huruf"
      ? [x.face, x.name, x.nameTr, x.sound, x.translit, x.type, x.exRu, x.exGloss].join(" ")
      : [x.prompt, x.promptRu].concat(x.options).join(" "),
    kind: (x) => (x.kind === "soal" ? "mcq" : "flip"),
    front(x) {
      if (x.kind === "soal") {
        return `<div class="prompt">${esc(x.prompt)}</div>
          ${x.promptRu ? ru(x.promptRu, "ru-lg") : ""}`;
      }
      return `<div class="ru ru-letter" lang="ru">${esc(x.face)}</div>
        <div class="hint" style="position:static;margin-top:10px">Bunyinya apa, dan namanya apa?</div>`;
    },
    back(x) {
      if (x.kind === "soal") {
        return `<div class="detail">${esc(x.catLabel)}</div>
          <div class="meaning">${x.optionsLang === "ru"
            ? `<span class="ru ru-md" lang="ru">${esc(x.options[x.answer])}</span>`
            : esc(x.options[x.answer])}</div>
          ${x.explain ? `<div class="note">${esc(x.explain)}</div>` : ""}`;
      }
      return `<div class="meaning">${esc(x.translit)} &mdash; ${esc(x.sound)}</div>
        <dl class="kv">
          <dt>Nama huruf</dt><dd><span class="ru ru-sm" lang="ru">${esc(x.name)}</span> (${esc(x.nameTr)})</dd>
          <dt>Jenis</dt><dd>${esc(x.type)}</dd>
          <dt>Kelompok</dt><dd>${esc(x.catLabel)}</dd>
        </dl>
        <hr class="sep" />
        <div class="example">${ru(x.exRu, "ru-md")}${tr(x.exTr)}${lafal(x.exLafal)}
          <div class="gloss">${esc(x.exGloss)}</div></div>
        ${x.note ? `<div class="note">${esc(x.note)}</div>` : ""}`;
    },
  },

  kosakata: {
    label: "Kosakata",
    toggles: ["tekanan", "arah"],
    items: () => D.kosakata,
    search: (x) => [x.ru, x.bare, x.tr, x.lafal, x.gloss, x.root, x.detail].concat(x.alt).join(" "),
    kind: () => "flip",
    front(x) {
      if (prefs.arah) {
        return `<div class="id-xl">${esc(x.gloss)}</div>
                <div class="tr">${esc(x.pos)}</div>`;
      }
      return ru(frontRu(x), "ru-xl") + tr(x.tr);
    },
    back(x) {
      return `<div class="meaning">${esc(x.gloss)}</div>
        <div class="detail">${esc(x.detail)}</div>
        ${prefs.arah ? ru(x.ru, "ru-lg") + tr(x.tr) : ""}
        ${lafal(x.lafal)}
        <hr class="sep" />
        <div class="example">${ru(x.exRu, "ru-md")}${tr(x.exTr)}${lafal(x.exLafal)}
          <div class="gloss">${esc(x.exGloss)}</div></div>
        ${x.note ? `<div class="note">${esc(x.note)}</div>` : ""}`;
    },
  },

  tatabahasa: {
    label: "Tata bahasa",
    toggles: [],
    items: () => D.tatabahasa,
    search: (x) => [x.prompt, x.promptRu, x.catLabel].concat(x.options).join(" "),
    kind: () => "mcq",
    front(x) {
      return `<div class="prompt">${esc(x.prompt)}</div>
        ${x.promptRu ? ru(x.promptRu, "ru-lg") + tr(x.promptTr) : ""}`;
    },
    back(x) {
      return `<div class="detail">${esc(x.catLabel)}</div>
        <div class="meaning">${x.optionsLang === "ru"
          ? `<span class="ru ru-md" lang="ru">${esc(x.options[x.answer])}</span>`
          : esc(x.options[x.answer])}</div>
        ${x.explain ? `<div class="note">${esc(x.explain)}</div>` : ""}`;
    },
  },

  akar: {
    label: "Akar kata",
    toggles: ["tekanan"],
    items: () => D.akar,
    search: (x) => [x.ru, x.bare, x.tr, x.gloss, x.root, x.pattern, x.rootMeaning].join(" "),
    kind: () => "flip",
    front(x) {
      return ru(frontRu(x), "ru-xl") + tr(x.tr) +
        `<div class="hint" style="position:static;margin-top:10px">Apa akarnya, dan afiks apa yang dipakai?</div>`;
    },
    back(x) {
      return `<div class="meaning">${esc(x.gloss)}</div>
        ${lafal(x.lafal)}
        <dl class="kv">
          <dt>Akar</dt><dd><span class="ru ru-sm" lang="ru">${esc(x.root)}</span> &mdash; ${esc(x.rootMeaning)}</dd>
          <dt>Afiks</dt><dd><span class="ru ru-sm" lang="ru">${esc(x.pattern)}</span></dd>
          ${x.variants.length ? `<dt>Varian akar</dt><dd><span class="ru ru-sm" lang="ru">${esc(x.variants.join(", "))}</span></dd>` : ""}
        </dl>
        ${x.siblings.length ? `<div class="sibs">Sekeluarga: ${
          x.siblings.map((s) => `<span class="ru" lang="ru">${esc(s)}</span>`).join(" &middot; ")
        }</div>` : ""}
        ${x.note ? `<div class="note">${esc(x.note)}</div>` : ""}`;
    },
  },

  baca: {
    label: "Tekanan & lafal",
    toggles: ["yo"],
    items: () => D.baca,
    search: (x) => [x.l1, x.l3, x.gloss, x.catLabel, x.prompt || ""].join(" "),
    kind: (x) => (x.kind === "soal" ? "mcq" : "flip"),
    front(x) {
      if (x.kind === "soal") {
        const body = ru(x.shown, "ru-lg");
        if (x.type === "stress_choice") {
          return body + `<div class="tr">kata yang ditanyakan:
            <span class="ru ru-sm" lang="ru">${esc(x.targetBare)}</span></div>`;
        }
        if (x.type === "pronounce_choice") {
          return `<div class="prompt">${esc(x.prompt)}</div>` + body;
        }
        return body + `<div class="tr">Apa arti kalimat ini?</div>`;
      }
      const teks = x.level === 1 ? x.l1 : x.level === 2 ? x.l2 : (prefs.yo ? x.l3NoYo : x.l3);
      return ru(teks, "ru-lg") +
        `<div class="hint" style="position:static;margin-top:10px">Baca dengan suara, tentukan letak tekanannya, lalu buka jawabannya</div>`;
    },
    back(x) {
      const glosses = (x.optionGlosses || []).length
        ? `<div class="note">Semua pilihan: ${x.options.map((o, i) =>
            `<span class="ru ru-sm" lang="ru">${esc(o)}</span> = ${esc(x.optionGlosses[i])}`).join("; ")}</div>`
        : "";
      return ru(x.l1, "ru-lg") + tr(x.tr) + lafal(x.lafal) +
        `<div class="gloss detail">${esc(x.gloss)}</div>
        ${x.explain ? `<div class="note">${esc(x.explain)}</div>` : ""}${glosses}`;
    },
  },

  palsu: {
    label: "Teman palsu",
    toggles: ["tekanan"],
    items: () => D.palsu,
    search: (x) => [x.ru, x.bare, x.tr, x.gloss, x.mistaken, x.correct, x.kind].join(" "),
    kind: () => "flip",
    front(x) {
      return ru(frontRu(x), "ru-xl") + tr(x.tr) +
        `<div class="hint" style="position:static;margin-top:10px">Apa artinya sebenarnya?</div>`;
    },
    back(x) {
      return `<div class="meaning">${esc(x.gloss)}</div>
        ${lafal(x.lafal)}
        <dl class="kv">
          <dt>Sering disangka</dt><dd>${esc(x.mistaken)}</dd>
          ${x.correct ? `<dt>Kata yang benar untuk sangkaan itu</dt><dd><span class="ru ru-sm" lang="ru">${esc(x.correct)}</span>${
            prefs.translit ? " (" + esc(x.correctTr) + ")" : ""}</dd>` : ""}
          <dt>Jenis</dt><dd>${esc(x.catLabel)}</dd>
        </dl>
        ${x.note ? `<div class="note">${esc(x.note)}</div>` : ""}`;
    },
  },
};

/* ------------------------------------------------------------ keadaan ---- */

let mode = "alfabet";
let deck = [];
let index = 0;
let activeCat = "*";
let activeStage = 0;
let query = "";
let shuffled = false;
let answered = false;

const els = {
  tabs: $("#tabs"), chips: $("#chips"), stages: $("#stages"), search: $("#search"),
  card: $("#card"), badge: $("#badge"), box: $("#box"), front: $("#front"),
  back: $("#back"), choices: $("#choices"), hint: $("#hint"),
  counter: $("#counter"), fill: $("#fill"), grade: $("#grade"),
  stats: $("#stats"), panel: $("#panel"),
};

/* ------------------------------------------------------------ susunan ---- */

function allItems() { return MODES[mode].items(); }

function buildDeck() {
  const cfg = MODES[mode];
  const q = query.trim().toLowerCase();
  deck = allItems().filter((x) => {
    if (activeCat !== "*" && x.cat !== activeCat) return false;
    if (activeStage && x.stage > activeStage) return false;
    if (prefs.due && !isDue(x.id)) return false;
    if (prefs.hide && boxOf(x.id) >= MAX_BOX) return false;
    if (q && !cfg.search(x).toLowerCase().includes(q)) return false;
    return true;
  });
  if (shuffled) {
    for (let i = deck.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [deck[i], deck[j]] = [deck[j], deck[i]];
    }
  }
  if (index >= deck.length) index = 0;
}

function renderChips() {
  const seen = new Map();
  for (const x of allItems()) {
    if (activeStage && x.stage > activeStage) continue;
    const prev = seen.get(x.cat) || { label: x.catLabel, n: 0 };
    prev.n += 1;
    seen.set(x.cat, prev);
  }
  const total = allItems().filter((x) => !activeStage || x.stage <= activeStage).length;
  let html = `<button data-cat="*" aria-pressed="${activeCat === "*"}">Semua<span class="n">${total}</span></button>`;
  for (const [cat, info] of seen) {
    html += `<button data-cat="${esc(cat)}" aria-pressed="${activeCat === cat}">${esc(info.label)}<span class="n">${info.n}</span></button>`;
  }
  els.chips.innerHTML = html;
}

function renderToggles() {
  const aktif = MODES[mode].toggles;
  $("#wrap-tekanan").hidden = !aktif.includes("tekanan");
  $("#wrap-arah").hidden = !aktif.includes("arah");
  $("#wrap-yo").hidden = !aktif.includes("yo");
}

/* ------------------------------------------------------------ tampilan ---- */

function render() {
  const cfg = MODES[mode];
  els.card.classList.remove("is-flipped");
  answered = false;

  if (!deck.length) {
    els.front.innerHTML = `<p class="empty">Tidak ada kartu yang cocok dengan saringan ini.<br />
      Coba hapus pencarian, pilih "Semua tahap", atau matikan "Jatuh tempo saja".</p>`;
    els.back.innerHTML = "";
    els.choices.hidden = true;
    els.grade.hidden = true;
    els.badge.textContent = "";
    els.box.textContent = "";
    els.counter.textContent = "0 / 0";
    els.fill.style.width = "0%";
    els.hint.textContent = "";
    return;
  }

  const x = deck[index];
  const kind = cfg.kind(x);

  els.badge.textContent = `${x.catLabel || ""} · tahap ${x.stage}`;
  const b = boxOf(x.id);
  els.box.textContent = b ? `kotak ${b}${isDue(x.id) ? " · jatuh tempo" : ""}` : "belum dilatih";

  els.front.innerHTML = cfg.front(x);
  els.back.innerHTML = cfg.back(x);

  if (kind === "mcq") {
    els.choices.hidden = false;
    els.choices.innerHTML = x.options.map((o, i) => {
      const isi = x.optionsLang === "ru"
        ? `<span class="opt-ru" lang="ru">${esc(o)}</span>`
        : esc(o);
      return `<button type="button" data-i="${i}"><span class="num">${i + 1}.</span>${isi}</button>`;
    }).join("");
    els.grade.hidden = true;
    els.hint.textContent = "Pilih satu jawaban (tekan 1–4)";
  } else {
    els.choices.hidden = true;
    els.choices.innerHTML = "";
    els.grade.hidden = false;
    els.hint.textContent = "Klik atau tekan Spasi untuk melihat jawaban";
  }

  els.counter.textContent = `${index + 1} / ${deck.length}`;
  els.fill.style.width = `${((index + 1) / deck.length) * 100}%`;
  renderPanel(x);
  fitCard();
}

/* Kedua sisi kartu diposisikan absolut, sehingga tingginya harus dihitung.
   Tanpa ini, kartu pilihan ganda yang panjang akan terpotong. */
function fitCard() {
  els.card.style.height = "auto";
  let h = 0;
  for (const face of els.card.querySelectorAll(".face")) {
    h = Math.max(h, face.scrollHeight);
  }
  // Sisa 4px supaya bilah gulir tidak muncul karena pembulatan.
  els.card.style.height = Math.max(300, h + 4) + "px";
}

function flip() {
  if (!deck.length) return;
  if (MODES[mode].kind(deck[index]) === "mcq" && !answered) return;
  els.card.classList.toggle("is-flipped");
}

function answer(i) {
  if (answered || !deck.length) return;
  const x = deck[index];
  if (MODES[mode].kind(x) !== "mcq") return;
  answered = true;
  const benar = i === x.answer;
  grade(x.id, benar);
  for (const btn of els.choices.querySelectorAll("button")) {
    const bi = Number(btn.dataset.i);
    btn.disabled = true;
    if (bi === x.answer) btn.classList.add("is-right");
    else if (bi === i) btn.classList.add("is-wrong");
  }
  els.hint.textContent = benar ? "Benar. Spasi untuk penjelasan." : "Belum tepat. Spasi untuk penjelasan.";
  els.box.textContent = `kotak ${boxOf(x.id)}`;
  renderStats();
}

function gradeFlip(ok) {
  if (!deck.length) return;
  grade(deck[index].id, ok);
  renderStats();
  next();
}

function next() { if (deck.length) { index = (index + 1) % deck.length; render(); } }
function prev() { if (deck.length) { index = (index - 1 + deck.length) % deck.length; render(); } }

/* -------------------------------------------------------------- panel ---- */

function renderPanel(x) {
  let html = "";
  if (mode === "tatabahasa") {
    const t = D.topik.find((t) => t.id === x.cat);
    if (t) {
      html = `<details open><summary>${esc(t.title)}</summary><div class="body">
        <p>${esc(t.explanation)}</p>
        ${t.examples.map((e) => `<div class="ru ru-sm" lang="ru">${esc(e.ru)}</div>
          ${prefs.lafal ? `<div class="lafal">${esc(e.lafal)}</div>` : ""}
          <p style="margin-top:2px">${esc(e.gloss)}</p>`).join("")}
        <p><strong>Pengecualian dan catatan:</strong></p>
        ${t.caveats.map((c) => `<div class="caveat">${esc(c)}</div>`).join("")}
      </div></details>`;
    }
  } else if (mode === "akar") {
    html = `<details><summary>Daftar awalan dan akhiran</summary><div class="body">
      ${D.afiks.map((p) => `<p><span class="ru ru-sm" lang="ru">${esc(p.affix)}</span>
        (${esc(p.type)}) — <strong>${esc(p.function)}</strong><br />
        ${p.examples.map((e) => `<span class="ru ru-sm" lang="ru">${esc(e.ru)}</span> ${esc(e.gloss)}`).join(" · ")}
        ${p.note ? `<br /><span style="opacity:.75">${esc(p.note)}</span>` : ""}</p>`).join("")}
    </div></details>
    <details><summary>Catatan tentang akar kata Rusia</summary><div class="body">
      ${D.catatan.akar.map((c) => `<p>${esc(c)}</p>`).join("")}
    </div></details>`;
  } else if (mode === "baca") {
    html = `<details><summary>Tiga level membaca</summary><div class="body">
      <ul>
        <li><strong>Level 1</strong> — ${esc(D.catatan.level["1"])}</li>
        <li><strong>Level 2</strong> — ${esc(D.catatan.level["2"])}</li>
        <li><strong>Level 3</strong> — ${esc(D.catatan.level["3"])}</li>
      </ul>
      ${D.catatan.baca.map((c) => `<p>${esc(c)}</p>`).join("")}
    </div></details>`;
  } else if (mode === "palsu") {
    html = `<details><summary>Yang perlu diingat tentang modul ini</summary><div class="body">
      ${D.catatan.palsu.map((c) => `<p>${esc(c)}</p>`).join("")}
      ${D.catatan.pemakaian.map((u) => `<p><strong>${esc(u.title)}.</strong> ${esc(u.text)}</p>`).join("")}
    </div></details>`;
  } else if (mode === "alfabet") {
    html = `<details><summary>Empat kelompok huruf</summary><div class="body">
      ${Object.keys(D.catatan.grup).map((k) =>
        `<p><strong>${esc(k)}</strong> — ${esc(D.catatan.grup[k])}</p>`).join("")}
    </div></details>`;
  }
  els.panel.innerHTML = html;
}

function renderStats() {
  const ids = allItems().map((x) => x.id);
  const kotak = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
  let baru = 0, jatuhTempo = 0, dilihat = 0, benar = 0;
  for (const id of ids) {
    const s = stateOf(id);
    if (!s) { baru += 1; continue; }
    kotak[s.box] += 1;
    dilihat += s.seen || 0;
    benar += s.right || 0;
    if (isDue(id)) jatuhTempo += 1;
  }
  const maxN = Math.max(1, ...Object.values(kotak));
  const baris = [1, 2, 3, 4, 5].map((b) =>
    `<tr><td>Kotak ${b}</td><td><span class="bar" style="width:${(kotak[b] / maxN) * 160}px"></span>
      &nbsp;${kotak[b]}</td></tr>`).join("");
  const pct = dilihat ? Math.round((benar / dilihat) * 100) : 0;
  els.stats.innerHTML = `<h3>Kemajuan pada modul ${esc(MODES[mode].label)}</h3>
    <table>
      <tr><td>Total kartu</td><td>${ids.length}</td></tr>
      <tr><td>Belum dilatih</td><td>${baru}</td></tr>
      <tr><td>Jatuh tempo</td><td>${jatuhTempo}</td></tr>
      ${baris}
    </table>
    <p>${dilihat ? `Jawaban tercatat: ${dilihat}, benar ${benar} (${pct}%).` : "Belum ada jawaban tercatat."}
    Jeda ulangan per kotak: 0, 1, 3, 7, dan 16 hari.</p>`;
}

/* ------------------------------------------------------------- kendali ---- */

function setMode(m) {
  mode = m;
  activeCat = "*";
  index = 0;
  answered = false;
  for (const b of els.tabs.querySelectorAll("button")) {
    b.setAttribute("aria-pressed", String(b.dataset.mode === m));
  }
  renderToggles();
  renderChips();
  buildDeck();
  render();
  renderStats();
}

function refresh() {
  renderChips();
  buildDeck();
  render();
}

function setTheme(name) {
  document.body.className = "theme-" + name;
  for (const b of document.querySelectorAll(".theme-dot")) {
    b.setAttribute("aria-pressed", String(b.dataset.theme === name));
  }
  lsSet(LS.theme, name);
}

function bindToggle(id, key) {
  const el = $(id);
  el.checked = prefs[key];
  el.addEventListener("change", () => {
    prefs[key] = el.checked;
    lsSet(LS.prefs, prefs);
    render();
  });
}

function init() {
  if (!D) {
    document.body.innerHTML = '<p class="empty">webdata.js gagal dimuat. ' +
      'Jalankan <code>python tools/build_web.py</code> lalu muat ulang halaman.</p>';
    return;
  }

  setTheme(lsGet(LS.theme, "bumaga"));

  els.tabs.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (b) setMode(b.dataset.mode);
  });
  els.chips.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    activeCat = b.dataset.cat;
    index = 0;
    refresh();
  });
  els.stages.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    activeStage = Number(b.dataset.stage);
    for (const s of els.stages.querySelectorAll("button")) {
      s.setAttribute("aria-pressed", String(Number(s.dataset.stage) === activeStage));
    }
    activeCat = "*";
    index = 0;
    refresh();
  });
  els.search.addEventListener("input", () => {
    query = els.search.value;
    index = 0;
    buildDeck();
    render();
  });
  els.choices.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (b) answer(Number(b.dataset.i));
  });
  els.card.addEventListener("click", (e) => {
    if (!e.target.closest(".choices")) flip();
  });

  $("#btn-flip").addEventListener("click", (e) => { e.stopPropagation(); flip(); });
  $("#btn-next").addEventListener("click", next);
  $("#btn-prev").addEventListener("click", prev);
  $("#btn-right").addEventListener("click", () => gradeFlip(true));
  $("#btn-wrong").addEventListener("click", () => gradeFlip(false));
  $("#btn-shuffle").addEventListener("click", (e) => {
    shuffled = !shuffled;
    e.currentTarget.setAttribute("aria-pressed", String(shuffled));
    index = 0;
    buildDeck();
    render();
  });
  $("#btn-stats").addEventListener("click", (e) => {
    const buka = els.stats.hidden;
    els.stats.hidden = !buka;
    e.currentTarget.setAttribute("aria-expanded", String(buka));
    if (buka) renderStats();
  });
  $("#btn-reset").addEventListener("click", () => {
    if (!confirm("Hapus seluruh progres di peramban ini? Tindakan ini tidak bisa dibatalkan.")) return;
    progress.cards = {};
    lsSet(LS.prog, progress);
    refresh();
    renderStats();
  });

  for (const b of document.querySelectorAll(".theme-dot")) {
    b.addEventListener("click", () => setTheme(b.dataset.theme));
  }

  bindToggle("#tg-translit", "translit");
  bindToggle("#tg-lafal", "lafal");
  bindToggle("#tg-tekanan", "tekanan");
  bindToggle("#tg-arah", "arah");
  bindToggle("#tg-yo", "yo");
  $("#tg-due").checked = prefs.due;
  $("#tg-due").addEventListener("change", () => {
    prefs.due = $("#tg-due").checked;
    lsSet(LS.prefs, prefs);
    index = 0;
    refresh();
  });
  $("#tg-hide").checked = prefs.hide;
  $("#tg-hide").addEventListener("change", () => {
    prefs.hide = $("#tg-hide").checked;
    lsSet(LS.prefs, prefs);
    index = 0;
    refresh();
  });

  document.addEventListener("keydown", (e) => {
    if (e.target === els.search) {
      if (e.key === "Escape") { els.search.value = ""; query = ""; index = 0; refresh(); els.search.blur(); }
      return;
    }
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    switch (e.key) {
      case " ": case "Enter": e.preventDefault(); flip(); break;
      case "ArrowRight": e.preventDefault(); next(); break;
      case "ArrowLeft": e.preventDefault(); prev(); break;
      case "h": case "H": gradeFlip(true); break;
      case "b": case "B": gradeFlip(false); break;
      case "s": case "S": $("#btn-shuffle").click(); break;
      case "t": case "T": $("#tg-translit").click(); break;
      case "l": case "L": $("#tg-lafal").click(); break;
      case "/": e.preventDefault(); els.search.focus(); break;
      default:
        if (/^[1-9]$/.test(e.key)) answer(Number(e.key) - 1);
    }
  });

  window.addEventListener("resize", fitCard);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitCard);

  setMode("alfabet");

  // Jumlah kartu pada tab diambil dari data, bukan ditulis tangan.
  for (const b of els.tabs.querySelectorAll("button")) {
    const n = MODES[b.dataset.mode].items().length;
    b.querySelector("span").textContent = String(n);
  }
}

document.addEventListener("DOMContentLoaded", init);

// Bemor sahifasi
const $ = (id) => document.getElementById(id);
let current = null;      // oxirgi javob
let maxQuestions = 3;

// Tana sohalari: karta bosilganda boshlang'ich ibora yoziladi, bemor davom ettiradi
const ICON = {
  head: '<circle cx="12" cy="9" r="5.5"/><path d="M9 14.5v2.5a3 3 0 0 0 6 0v-2.5"/>',
  chest: '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
  stomach: '<path d="M9 3v4c0 2-3 3-3 7a6 6 0 0 0 12 0c0-3-2-4-4-4h-1V3"/>',
  back: '<path d="M12 3v18"/><path d="M8.5 6h7M8 10h8M8.5 14h7M9 18h6"/>',
  leg: '<path d="M10 3v8l-2 9h4l2-6 1 6h3l-2-10V3"/>',
  skin: '<rect x="4" y="4" width="16" height="16" rx="5"/><circle cx="9" cy="10" r="1.2"/><circle cx="14.5" cy="9" r="1"/><circle cx="12" cy="14.5" r="1.4"/>',
  ent: '<path d="M16 9a4 4 0 1 0-8 0c0 2.5 2 3 2 5.5a2.5 2.5 0 0 0 5 0"/><path d="M12 9.5a1.5 1.5 0 0 1 1.5 1.5"/>',
  child: '<circle cx="12" cy="6" r="3"/><path d="M7 21l1.5-7h7L17 21M8 12l4-2 4 2"/>',
  lab: '<path d="M10 3h4M11 3v6l-5 9a2 2 0 0 0 1.8 3h8.4a2 2 0 0 0 1.8-3l-5-9V3"/><path d="M8.5 15h7"/>',
};
const AREAS = [
  ["head", { uz: "Bosh", ru: "Голова" }, { uz: "Boshim og'riyapti", ru: "Болит голова" }],
  ["chest", { uz: "Ko'krak, yurak", ru: "Грудь, сердце" }, { uz: "Ko'kragim og'riyapti", ru: "Болит в груди" }],
  ["stomach", { uz: "Qorin", ru: "Живот" }, { uz: "Qornim og'riyapti", ru: "Болит живот" }],
  ["back", { uz: "Bel, umurtqa", ru: "Спина, поясница" }, { uz: "Belim og'riyapti", ru: "Болит поясница" }],
  ["leg", { uz: "Qo'l-oyoq, bo'g'im", ru: "Руки, ноги, суставы" }, { uz: "Oyog'im og'riyapti", ru: "Болит нога" }],
  ["skin", { uz: "Teri", ru: "Кожа" }, { uz: "Terimda toshma chiqdi", ru: "Сыпь на коже" }],
  ["ent", { uz: "Quloq, tomoq, burun", ru: "Ухо, горло, нос" }, { uz: "Tomog'im og'riyapti", ru: "Болит горло" }],
  ["child", { uz: "Bola", ru: "Ребёнок" }, { uz: "Bolamning isitmasi bor", ru: "У ребёнка температура" }],
  ["lab", { uz: "Tahlillar", ru: "Анализы" }, { uz: "Qon tahlili topshirmoqchiman", ru: "Хочу сдать анализ крови" }],
];
const svg = (k) => `<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7"
  stroke-linecap="round" stroke-linejoin="round">${ICON[k]}</svg>`;

function renderAreas() {
  $("area-grid").innerHTML = AREAS.map(([k, label]) =>
    `<button type="button" class="area" data-area="${k}">${svg(k)}<span>${esc(label[LANG])}</span></button>`).join("");
  $("area-grid").querySelectorAll(".area").forEach((b) => b.addEventListener("click", () => {
    const phrase = AREAS.find((a) => a[0] === b.dataset.area)[2][LANG];
    const ta = $("complaint");
    ta.value = ta.value.trim() ? `${ta.value.trim()}, ${phrase.toLowerCase()}` : phrase;
    updateCounter(); ta.focus(); ta.setSelectionRange(ta.value.length, ta.value.length);
  }));
}

function updateCounter() { $("counter").textContent = `${$("complaint").value.length} / 1500`; }

function ring(p) {
  const r = 30, c = 2 * Math.PI * r, v = Math.max(0, Math.min(1, p));
  return `<div class="ring" role="img" aria-label="${t("confidence")}: ${pct(v)}">
    <svg viewBox="0 0 72 72"><circle class="ring-bg" cx="36" cy="36" r="${r}"/>
    <circle class="ring-fg" cx="36" cy="36" r="${r}" stroke-dasharray="${(c * v).toFixed(1)} ${c.toFixed(1)}"/></svg>
    <b>${pct(v)}</b></div>`;
}

function trace(r) {
  const items = [];
  const first = r.steps.find((s) => s.step === "model");
  const name = (d) => (r.top.find((x) => x.dept === d)?.name?.[LANG]) || d;
  if (r.steps.some((s) => s.step === "explicit")) items.push(t("t_explicit"));
  else if (first) items.push(t("t_model")(name(first.dept), pct(first.p)));
  r.answers.forEach((a) => items.push(t("t_answer")(a.question[LANG], a.text[LANG])));
  if (r.status === "routed" && r.department) items.push(t("t_final")(name(r.department), pct(r.confidence)));
  return `<details class="card trace"><summary>${t("trace")}</summary>
    <ol class="timeline">${items.map((i) => `<li>${esc(i)}</li>`).join("")}</ol></details>`;
}

function info(kind, title, body) {
  return `<article class="card info info-${kind}"><span class="info-dot" aria-hidden="true"></span>
    <div><h2>${title}</h2>${body}</div></article>`;
}

function render(r) {
  current = r;
  const out = [];
  if (r.crisis) {
    out.push(`<article class="card alert crisis"><h2>${t("crisis_title")}</h2><p>${esc(r.crisis[LANG])}</p></article>`);
  } else if (r.urgent) {
    out.push(`<article class="card alert"><h2>${t("urgent_title")}</h2>
      <p>${esc(r.flags_text.map((f) => f[LANG]).join("; "))}</p><p class="alert-call">${t("urgent_text")}</p></article>`);
  }

  if (r.status === "routed") {
    const top = r.top.find((x) => x.dept === r.department) || r.top[0];
    const alts = r.top.filter((x) => x.dept !== r.department && x.dept !== "boshqa" && x.p >= 0.05);
    out.push(`<article class="ticket">
      <div class="ticket-main">
        <p class="ticket-label">${t("go_to")}</p>
        <h2 class="dept" tabindex="-1">${esc(top.name[LANG])}</h2>
        <p class="reason">${esc(r.reason[LANG])}</p>
        ${alts.length ? `<p class="alts-label">${t("alts")}</p><div class="alts">${alts.map((a) =>
          `<div class="alt"><span>${esc(a.name[LANG])}</span><b>${pct(a.p)}</b></div>`).join("")}</div>` : ""}
      </div>
      <div class="ticket-stub">
        ${ring(r.confidence)}
        <div class="stub-text"><span class="stub-label">${t("confidence")}</span>
        ${r.case_id ? `<span class="stub-no">${t("ticket_no")} ${String(r.case_id).padStart(4, "0")}</span>` : ""}</div>
      </div>
    </article>`);
    out.push(trace(r));
  } else if (r.status === "question") {
    const q = r.question, n = r.answers.length + 1;
    const dots = Array.from({ length: maxQuestions }, (_, i) =>
      `<span class="${i < n - 1 ? "done" : i === n - 1 ? "now" : ""}"></span>`).join("");
    const opts = q.options.filter((o) => o.id !== "unknown"), unk = q.options.find((o) => o.id === "unknown");
    out.push(`<article class="card question">
      <div class="q-head"><div class="dots" aria-hidden="true">${dots}</div>
        <span class="progress">${t("q_progress")(n, maxQuestions)}</span></div>
      <h2 tabindex="-1">${esc(q.text[LANG])}</h2>
      <p class="q-hint">${t("q_hint")}</p>
      <div class="options">${opts.map((o) =>
        `<button type="button" class="option" data-opt="${esc(o.id)}">${esc(o.text[LANG])}</button>`).join("")}</div>
      ${unk ? `<button type="button" class="option-unknown" data-opt="unknown">${esc(unk.text[LANG])}</button>` : ""}
    </article>`);
  } else if (r.status === "other") {
    out.push(info("other", t("other_title"),
      `${r.other?.advice ? `<p>${t("other_text")} <b>${esc(r.other.advice[LANG])}</b>.</p>` : ""}<p class="muted">${t("operator_text")}</p>`));
  } else if (r.status === "not_medical") {
    out.push(info("neutral", t("nm_title"), `<p class="muted">${esc(r.reason[LANG])}</p>`));
  } else {
    out.push(info("operator", t("operator_title"),
      `<p class="muted">${esc(r.reason[LANG])}</p><p>${t("operator_text")}</p>`));
    if (r.top.length) out.push(trace(r));
  }

  $("result").innerHTML = out.join("");
  $("result").querySelectorAll("[data-opt]").forEach((b) => b.addEventListener("click", () => answer(b.dataset.opt, b)));
  showSummary(true);
  const focusTarget = $("result").querySelector(".question h2, .dept, .info h2");
  if (focusTarget) focusTarget.focus({ preventScroll: true });
  $("summary").scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
}

function showSummary(on) {
  $("form").hidden = on; $("areas").hidden = on; $("hero").hidden = on;
  $("summary").hidden = !on;
  if (on) $("summary-text").textContent = $("complaint").value.trim();
}

async function send(path, body, btn) {
  $("error").hidden = true; $("submit").disabled = true; $("submit").textContent = t("wait");
  $("result").querySelectorAll("[data-opt]").forEach((b) => { b.disabled = true; });
  if (btn) btn.classList.add("picked");
  try { render(await api(path, { method: "POST", body: JSON.stringify(body) })); }
  catch (e) {
    showSummary(false); $("error").textContent = t("err"); $("error").hidden = false;
  }
  finally { $("submit").disabled = false; $("submit").textContent = t("submit"); }
}

function answer(opt, btn) {
  send("/api/answer", { case_id: current.case_id, question_id: current.question.id, option_id: opt }, btn);
}

$("form").addEventListener("submit", (e) => {
  e.preventDefault();
  const text = $("complaint").value.trim();
  if (!text) { $("error").textContent = t("empty_text"); $("error").hidden = false; $("complaint").focus(); return; }
  send("/api/triage", { text, lang: LANG });
});
$("complaint").addEventListener("input", updateCounter);
$("complaint").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) $("form").requestSubmit();
});
$("reset").addEventListener("click", () => {
  current = null; $("result").innerHTML = ""; $("complaint").value = ""; updateCounter();
  showSummary(false); $("complaint").focus();
});

initLang(() => { renderAreas(); if (current) render(current); });
renderAreas();
api("/api/info").then((i) => { maxQuestions = i.max_questions || maxQuestions; }).catch(() => {});

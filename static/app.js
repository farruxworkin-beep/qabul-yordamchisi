// Bemor sahifasi
const $ = (id) => document.getElementById(id);
let current = null;      // oxirgi javob
let maxQuestions = 3;

function renderExamples() {
  $("examples").innerHTML = t("examples")
    .map((e) => `<button type="button" class="chip">${esc(e)}</button>`).join("");
  $("examples").querySelectorAll(".chip").forEach((c) => c.addEventListener("click", () => {
    $("complaint").value = c.textContent; $("complaint").focus();
  }));
}

function meter(p) {
  return `<div class="meter-row"><div class="meter" role="img" aria-label="${pct(p)}"><span style="width:${pct(p)}"></span></div>
          <span class="pct">${pct(p)}</span></div>`;
}

function trace(r) {
  const items = [];
  const first = r.steps.find((s) => s.step === "model");
  const name = (d) => (r.top.find((x) => x.dept === d)?.name?.[LANG]) || d;
  if (r.steps.some((s) => s.step === "explicit")) items.push(t("t_explicit"));
  else if (first) items.push(t("t_model")(name(first.dept), pct(first.p)));
  r.answers.forEach((a) => items.push(t("t_answer")(a.question[LANG], a.text[LANG])));
  if (r.status === "routed" && r.department) items.push(t("t_final")(name(r.department), pct(r.confidence)));
  return `<details class="trace"><summary>${t("trace")}</summary><ol>${items.map((i) => `<li>${esc(i)}</li>`).join("")}</ol></details>`;
}

function render(r) {
  current = r;
  const out = [];
  if (r.crisis) {
    out.push(`<div class="panel crisis"><h2>${t("crisis_title")}</h2><p>${esc(r.crisis[LANG])}</p></div>`);
  } else if (r.urgent) {
    out.push(`<div class="panel urgent"><h2>${t("urgent_title")}</h2>
      <p>${esc(r.flags_text.map((f) => f[LANG]).join("; "))}</p><p>${t("urgent_text")}</p></div>`);
  }

  if (r.status === "routed") {
    const top = r.top.find((x) => x.dept === r.department) || r.top[0];
    const alts = r.top.filter((x) => x.dept !== r.department && x.dept !== "boshqa" && x.p >= 0.05);
    out.push(`<div class="panel">
      <p class="dept-label">${t("go_to")}</p>
      <p class="dept">${esc(top.name[LANG])}</p>
      <p class="dept-label">${t("confidence")}</p>${meter(r.confidence)}
      <p class="reason">${esc(r.reason[LANG])}</p>
      ${alts.length ? `<p class="dept-label" style="margin-top:14px">${t("alts")}</p><ul class="alts">${alts.map((a) =>
        `<li><span>${esc(a.name[LANG])}</span><div class="meter"><span style="width:${pct(a.p)}"></span></div><span class="pct">${pct(a.p)}</span></li>`).join("")}</ul>` : ""}
      ${trace(r)}</div>`);
  } else if (r.status === "question") {
    const q = r.question, n = r.answers.length + 1;
    out.push(`<div class="panel question">
      <p class="progress">${t("q_progress")(n, maxQuestions)}</p>
      <h2>${esc(q.text[LANG])}</h2>
      <div class="options">${q.options.map((o) =>
        `<button type="button" class="option${o.id === "unknown" ? " muted" : ""}" data-opt="${esc(o.id)}">${esc(o.text[LANG])}</button>`).join("")}</div>
      </div>`);
  } else if (r.status === "other") {
    out.push(`<div class="panel"><h2>${t("other_title")}</h2>
      ${r.other?.advice ? `<p>${t("other_text")} <b>${esc(r.other.advice[LANG])}</b>.</p>` : ""}
      <p class="reason">${t("operator_text")}</p></div>`);
  } else if (r.status === "not_medical") {
    out.push(`<div class="panel"><h2>${t("nm_title")}</h2><p class="reason">${esc(r.reason[LANG])}</p></div>`);
  } else {
    out.push(`<div class="panel"><h2>${t("operator_title")}</h2><p class="reason">${esc(r.reason[LANG])}</p>
      <p>${t("operator_text")}</p>${r.top.length ? trace(r) : ""}</div>`);
  }
  $("result").innerHTML = out.join("");
  $("reset").hidden = false;
  $("result").querySelectorAll(".option").forEach((b) => b.addEventListener("click", () => answer(b.dataset.opt)));
  const focusTarget = $("result").querySelector(".option, h2, .dept");
  if (focusTarget && r.status === "question") focusTarget.focus();
}

async function send(path, body) {
  $("error").hidden = true; $("submit").disabled = true; $("submit").textContent = t("wait");
  try { render(await api(path, { method: "POST", body: JSON.stringify(body) })); }
  catch (e) { $("error").textContent = t("err"); $("error").hidden = false; }
  finally { $("submit").disabled = false; $("submit").textContent = t("submit"); }
}

function answer(opt) {
  send("/api/answer", { case_id: current.case_id, question_id: current.question.id, option_id: opt });
}

$("form").addEventListener("submit", (e) => {
  e.preventDefault();
  const text = $("complaint").value.trim();
  if (!text) { $("error").textContent = t("empty_text"); $("error").hidden = false; return; }
  send("/api/triage", { text, lang: LANG });
});
$("reset").addEventListener("click", () => {
  current = null; $("result").innerHTML = ""; $("complaint").value = ""; $("reset").hidden = true; $("complaint").focus();
});

initLang(() => { renderExamples(); if (current) render(current); });
renderExamples();
api("/api/info").then((i) => { maxQuestions = i.max_questions; }).catch(() => {});

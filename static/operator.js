// Operator paneli
const $ = (id) => document.getElementById(id);
let DEPTS = {}, showAll = false, cases = [];

function fmtTime(iso) {
  try { return new Date(iso).toLocaleString(LANG === "ru" ? "ru-RU" : "uz-UZ", { dateStyle: "short", timeStyle: "short" }); }
  catch (e) { return iso; }
}

function caseHtml(c) {
  const r = c.result || {}, done = !!c.operator_dept;
  const kind = c.urgent ? "is-urgent" : (c.status === "other" ? "is-other" : "");
  const tags = [];
  if (c.urgent) tags.push(`<span class="tag red">${t("st_urgent")}</span>`);
  tags.push(`<span class="tag ${c.status === "other" ? "amber" : "green"}">${t("st_" + c.status) || c.status}</span>`);
  if (done) tags.push(`<span class="tag green">${t("confirmed")}: ${esc(DEPTS[c.operator_dept]?.[LANG] || c.operator_dept)}</span>`);
  const ai = (r.top || []).map((x) => `<li><span>${esc(x.name[LANG])}</span>
    <div class="meter"><span style="width:${pct(x.p)}"></span></div><b class="mono">${pct(x.p)}</b></li>`).join("");
  const answers = (c.answers_text || []).length
    ? `<div class="case-ai">${t("answers")}: ${c.answers_text.map((a) => esc(a.question[LANG] + " — " + a.answer[LANG])).join("; ")}</div>` : "";
  const flags = (r.flags_text || []).map((f) => esc(f[LANG])).join("; ");
  const options = Object.entries(DEPTS).map(([k, v]) =>
    `<option value="${k}" ${k === (c.operator_dept || r.department) ? "selected" : ""}>${esc(v[LANG])}</option>`).join("");
  return `<article class="case ${kind} ${done ? "is-done" : ""}" data-id="${c.id}">
    <div class="case-head"><span class="case-id">#${c.id}</span><span>${fmtTime(c.created)}</span>${tags.join("")}</div>
    <p class="case-text">${esc(c.text)}</p>
    ${flags ? `<div class="case-flags">${flags}</div>` : ""}
    <div class="case-ai">${t("ai_says")}</div>${ai ? `<ul class="case-top">${ai}</ul>` : "<div class=\"case-ai\">—</div>"}${answers}
    <form class="case-form">
      <select aria-label="${t("choose_dept")}" name="dept">${options}</select>
      <input name="note" placeholder="${t("note_ph")}" maxlength="500" value="${esc(c.operator_note || "")}">
      <button class="btn" type="submit">${t("confirm")}</button>
    </form></article>`;
}

function render() {
  $("cases").innerHTML = cases.length ? cases.map(caseHtml).join("") : `<p class="empty">${t("no_cases")}</p>`;
  $("cases").querySelectorAll(".case-form").forEach((f) => f.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = f.closest(".case").dataset.id;
    await api(`/api/cases/${id}/resolve`, { method: "POST",
      body: JSON.stringify({ department: f.dept.value, note: f.note.value || null }) });
    load();
  }));
}

async function load() {
  try { cases = await api(`/api/queue?resolved=${showAll}`); render(); }
  catch (e) { if (e.status === 401) showLogin(); }
}

function showLogin() { $("panel").hidden = true; $("login").hidden = false; $("pw").focus(); }
async function showPanel() {
  $("login").hidden = true; $("panel").hidden = false;
  DEPTS = await api("/api/departments"); load();
}

$("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  try { await api("/api/login", { method: "POST", body: JSON.stringify({ password: $("pw").value }) }); $("pw").value = ""; showPanel(); }
  catch (err) { $("login-error").textContent = t("wrong_pw"); $("login-error").hidden = false; }
});
$("logout").addEventListener("click", async () => { await api("/api/logout", { method: "POST" }); showLogin(); });
$("refresh").addEventListener("click", load);
[["f-pending", false], ["f-all", true]].forEach(([id, v]) => $(id).addEventListener("click", () => {
  showAll = v; $("f-pending").setAttribute("aria-pressed", !v); $("f-all").setAttribute("aria-pressed", v); load();
}));

initLang(render);
api("/api/me").then(showPanel).catch(showLogin);
setInterval(() => { if (!$("panel").hidden) load(); }, 20000);

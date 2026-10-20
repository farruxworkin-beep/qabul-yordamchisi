// Umumiy: til almashtirish va API yordamchilari
const I18N = {
  uz: {
    brand: "Qabul yordamchisi", nav_patient: "Murojaat", nav_operator: "Operator", nav_stats: "Statistika",
    h1: "Nima bezovta qilyapti?",
    lead: "Shikoyatingizni o'z so'zlaringiz bilan yozing — qaysi bo'limga murojaat qilishni aytamiz.",
    placeholder: "Masalan: ikki kundan beri boshim qattiq og'riyapti, ko'nglim aynayapti",
    examples: ["Bel og'rig'i", "Bolamning isitmasi 39", "Tomog'im og'rib, yutolmayapman", "Qon tahlili topshirmoqchiman"],
    area_title: "Qayeringiz bezovta qilyapti?", area_hint: "Sohani tanlang, keyin batafsilroq yozing: qachondan beri, qanday og'riydi.",
    your_complaint: "Sizning murojaatingiz", ticket_no: "Murojaat №", q_hint: "Sizga mos javobni tanlang",
    sos: "Ahvol og'ir bo'lsa, kutmang — tez yordam chaqiring",
    submit: "Bo'limni aniqlash", wait: "Aniqlanmoqda…", reset: "Yangi murojaat",
    go_to: "Sizga mos bo'lim", confidence: "Tizim ishonchi", alts: "Boshqa ehtimoliy bo'limlar",
    urgent_title: "Diqqat: xavfli belgi", urgent_text: "Ahvolingiz og'irlashsa, kutmang — 103 ga qo'ng'iroq qiling.",
    crisis_title: "Yordam yaqin",
    operator_title: "Murojaatingizni operator ko'rib chiqadi", operator_text: "Tez orada siz bilan bog'lanamiz yoki qabulxonaga murojaat qiling.",
    other_title: "Bu yo'nalish shifoxonamizda yo'q", other_text: "Sizga kerak bo'lishi mumkin:",
    nm_title: "Shikoyatingizni yozing",
    q_progress: (n, m) => `Aniqlashtiruvchi savol ${n} / ${m}`,
    trace: "Qanday aniqlandi", t_model: (d, p) => `Matn tahlili: ${d} — ${p}`,
    t_answer: (q, a) => `«${q}» — ${a}`, t_final: (d, p) => `Natija: ${d} — ${p}`,
    t_explicit: "Siz bo'limni o'zingiz ko'rsatdingiz",
    note: "Bu tizim tashxis qo'ymaydi — faqat qaysi bo'limga murojaat qilishni tavsiya qiladi.",
    empty_text: "Iltimos, shikoyatingizni yozing.", err: "Xatolik yuz berdi. Qayta urinib ko'ring.",
    // operator
    login_title: "Operator paneli", password: "Parol", login: "Kirish", logout: "Chiqish", wrong_pw: "Parol noto'g'ri",
    pending: "Kutilmoqda", all: "Hammasi", export: "CSV yuklab olish", refresh: "Yangilash",
    no_cases: "Hozircha ko'rib chiqiladigan murojaat yo'q.", ai_says: "AI tavsiyasi",
    choose_dept: "To'g'ri bo'limni tanlang", note_ph: "Izoh (ixtiyoriy)", confirm: "Tasdiqlash", confirmed: "Tasdiqlandi",
    st_operator: "operator", st_other: "boshqa yo'nalish", st_routed: "yo'naltirilgan", st_urgent: "shoshilinch",
    answers: "Javoblar",
    // stats
    stats_title: "Statistika", s_total: "Jami murojaat", s_auto: "Avtomatik yo'naltirildi", s_operator: "Operatorga",
    s_urgent: "Shoshilinch", s_questions: "Savol berilgan", s_agree: "Operator AI bilan kelishdi",
    s_by_dept: "Bo'limlar bo'yicha", s_model: "Model", s_pending: "Kutilayotgan",
  },
  ru: {
    brand: "Помощник регистратуры", nav_patient: "Обращение", nav_operator: "Оператор", nav_stats: "Статистика",
    h1: "Что вас беспокоит?",
    lead: "Опишите жалобу своими словами — подскажем, в какое отделение обратиться.",
    placeholder: "Например: второй день сильно болит голова и тошнит",
    examples: ["Боль в пояснице", "У ребёнка температура 39", "Болит горло, трудно глотать", "Хочу сдать анализ крови"],
    area_title: "Где беспокоит?", area_hint: "Выберите область и допишите подробнее: как давно, какая боль.",
    your_complaint: "Ваше обращение", ticket_no: "Обращение №", q_hint: "Выберите подходящий ответ",
    sos: "Если состояние тяжёлое, не ждите — вызовите скорую",
    submit: "Определить отделение", wait: "Определяем…", reset: "Новое обращение",
    go_to: "Подходящее отделение", confidence: "Уверенность системы", alts: "Другие возможные отделения",
    urgent_title: "Внимание: тревожный признак", urgent_text: "Если состояние ухудшается, не ждите — звоните 103.",
    crisis_title: "Помощь рядом",
    operator_title: "Ваше обращение рассмотрит оператор", operator_text: "Мы скоро свяжемся с вами, или обратитесь в регистратуру.",
    other_title: "Такого направления в нашей клинике нет", other_text: "Возможно, вам нужен:",
    nm_title: "Опишите жалобу",
    q_progress: (n, m) => `Уточняющий вопрос ${n} из ${m}`,
    trace: "Как определено", t_model: (d, p) => `Анализ текста: ${d} — ${p}`,
    t_answer: (q, a) => `«${q}» — ${a}`, t_final: (d, p) => `Итог: ${d} — ${p}`,
    t_explicit: "Вы сами указали отделение",
    note: "Система не ставит диагноз — только подсказывает, в какое отделение обратиться.",
    empty_text: "Пожалуйста, опишите жалобу.", err: "Произошла ошибка. Попробуйте ещё раз.",
    login_title: "Панель оператора", password: "Пароль", login: "Войти", logout: "Выйти", wrong_pw: "Неверный пароль",
    pending: "Ожидают", all: "Все", export: "Скачать CSV", refresh: "Обновить",
    no_cases: "Пока нет обращений для проверки.", ai_says: "Подсказка ИИ",
    choose_dept: "Выберите правильное отделение", note_ph: "Комментарий (необязательно)", confirm: "Подтвердить", confirmed: "Подтверждено",
    st_operator: "оператор", st_other: "другое направление", st_routed: "направлено", st_urgent: "срочно",
    answers: "Ответы",
    stats_title: "Статистика", s_total: "Всего обращений", s_auto: "Направлено автоматически", s_operator: "Оператору",
    s_urgent: "Срочные", s_questions: "С уточняющими вопросами", s_agree: "Оператор согласился с ИИ",
    s_by_dept: "По отделениям", s_model: "Модель", s_pending: "Ожидают",
  },
};

function getLang() {
  try { return localStorage.getItem("lang") || "uz"; } catch (e) { return "uz"; }
}
let LANG = getLang();
const t = (k) => I18N[LANG][k];
const pct = (p) => `${Math.round(p * 100)}%`;
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function applyStatic() {
  document.documentElement.lang = LANG;
  document.querySelectorAll("[data-t]").forEach((el) => { el.textContent = t(el.dataset.t); });
  document.querySelectorAll("[data-t-ph]").forEach((el) => { el.placeholder = t(el.dataset.tPh); });
  document.querySelectorAll(".lang button").forEach((b) => b.setAttribute("aria-pressed", b.dataset.lang === LANG));
}

function initLang(onChange) {
  document.querySelectorAll(".lang button").forEach((b) => b.addEventListener("click", () => {
    LANG = b.dataset.lang;
    try { localStorage.setItem("lang", LANG); } catch (e) { /* ixtiyoriy */ }
    applyStatic(); onChange && onChange();
  }));
  applyStatic();
}

async function api(path, opts = {}) {
  const r = await fetch(path, { headers: { "Content-Type": "application/json" }, credentials: "same-origin", ...opts });
  if (!r.ok) { const e = new Error(r.status); e.status = r.status; throw e; }
  return r.json();
}

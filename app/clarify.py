"""
Aniqlashtiruvchi savollar.

Savollar banki shifokor mantiqi asosida qo'lda tuzilgan (xavfsiz, tushuntirib bo'ladigan).
AI qaror qiladi:
  1) QACHON so'rash kerak  — ensemble ishonchi chegaradan past bo'lsa;
  2) QAYSI savolni berish  — eng katta axborot yutug'i (entropiya kamayishi) beradiganini;
  3) javobni QANDAY hisobga olish — Bayes formulasi: P(bo'lim|javob) ∝ P(bo'lim)·P(javob|bo'lim).

LIK[bo'lim] = har bir javob varianti uchun P(javob | bo'lim). Ro'yxatda yo'q bo'lim uchun
barcha variantlar teng ehtimolli (savol u bo'lim haqida ma'lumot bermaydi).
"""
import numpy as np

QUESTIONS = [
    {
        "id": "abdomen_where",
        "text": {"uz": "Og'riq qorinning qaysi qismida?", "ru": "В какой части живота боль?"},
        "options": [
            {"id": "upper", "uz": "Yuqori qismida (to'sh ostida)", "ru": "Вверху (под грудиной)"},
            {"id": "navel", "uz": "Kindik atrofida", "ru": "Вокруг пупка"},
            {"id": "lower", "uz": "Pastki qismida", "ru": "Внизу живота"},
            {"id": "side", "uz": "Yon tomonda, belga yaqin", "ru": "Сбоку, ближе к пояснице"},
        ],
        "lik": {"gastroenterologiya": [.45, .30, .15, .10], "ginekologiya_urologiya": [.03, .07, .55, .35],
                "kardiologiya": [.85, .05, .05, .05], "travmatologiya": [.10, .10, .25, .55]},
    },
    {
        "id": "back_where",
        "text": {"uz": "Bel og'rig'i qanday?", "ru": "Какая боль в пояснице?"},
        "options": [
            {"id": "spine", "uz": "Umurtqa bo'ylab, egilganda kuchayadi", "ru": "По позвоночнику, сильнее при наклоне"},
            {"id": "leg", "uz": "Oyoqqa tarqaladi, oyoq uvishadi", "ru": "Отдаёт в ногу, нога немеет"},
            {"id": "kidney", "uz": "Yon tomonda, siyish o'zgargan", "ru": "Сбоку, изменилось мочеиспускание"},
            {"id": "injury", "uz": "Jarohat yoki og'ir ko'tarishdan keyin boshlandi", "ru": "Началась после травмы или подъёма тяжести"},
        ],
        "lik": {"travmatologiya": [.40, .12, .03, .45], "nevrologiya": [.25, .65, .03, .07],
                "ginekologiya_urologiya": [.05, .05, .85, .05], "terapiya": [.40, .20, .30, .10]},
    },
    {
        "id": "urine",
        "text": {"uz": "Siyishda o'zgarish bormi (achishish, tez-tez siyish, qon)?",
                 "ru": "Есть изменения при мочеиспускании (жжение, частые позывы, кровь)?"},
        "options": [{"id": "yes", "uz": "Ha", "ru": "Да"}, {"id": "no", "uz": "Yo'q", "ru": "Нет"}],
        "lik": {"ginekologiya_urologiya": [.85, .15], "gastroenterologiya": [.08, .92], "travmatologiya": [.05, .95],
                "nevrologiya": [.08, .92], "terapiya": [.20, .80], "pediatriya": [.15, .85]},
    },
    {
        "id": "cycle",
        "text": {"uz": "Og'riq hayz sikli yoki homiladorlik bilan bog'liqmi?",
                 "ru": "Связана ли боль с менструальным циклом или беременностью?"},
        "options": [{"id": "yes", "uz": "Ha", "ru": "Да"}, {"id": "no", "uz": "Yo'q", "ru": "Нет"},
                    {"id": "male", "uz": "Men erkakman", "ru": "Я мужчина"}],
        "lik": {"ginekologiya_urologiya": [.60, .25, .15], "gastroenterologiya": [.05, .55, .40],
                "travmatologiya": [.03, .50, .47], "terapiya": [.05, .50, .45]},
    },
    {
        "id": "injury",
        "text": {"uz": "Bundan oldin yiqilish, zarba yoki og'ir ko'tarish bo'lganmi?",
                 "ru": "Перед этим было падение, удар или подъём тяжести?"},
        "options": [{"id": "yes", "uz": "Ha", "ru": "Да"}, {"id": "no", "uz": "Yo'q", "ru": "Нет"}],
        "lik": {"travmatologiya": [.85, .15], "nevrologiya": [.15, .85], "terapiya": [.05, .95],
                "kardiologiya": [.03, .97], "ginekologiya_urologiya": [.03, .97], "dermatologiya": [.05, .95],
                "gastroenterologiya": [.03, .97]},
    },
    {
        "id": "chest_type",
        "text": {"uz": "Ko'krakdagi og'riq qanday?", "ru": "Какая боль в груди?"},
        "options": [
            {"id": "press", "uz": "Siquvchi, yurganda kuchayadi", "ru": "Давящая, сильнее при ходьбе"},
            {"id": "food", "uz": "Ovqatdan keyin achishadi, kekirish bor", "ru": "Жжёт после еды, есть отрыжка"},
            {"id": "breath", "uz": "Nafas olganda yoki bosganda sanchiydi", "ru": "Колет при вдохе или надавливании"},
            {"id": "beat", "uz": "Yurak tez yoki notekis uradi", "ru": "Сердце бьётся часто или неровно"},
        ],
        "lik": {"kardiologiya": [.45, .05, .15, .35], "gastroenterologiya": [.05, .85, .05, .05],
                "travmatologiya": [.05, .05, .85, .05], "nevrologiya": [.10, .05, .30, .55],
                "terapiya": [.15, .10, .50, .25]},
    },
    {
        "id": "dizzy",
        "text": {"uz": "Bosh aylanishi qanday kechadi?", "ru": "Как проявляется головокружение?"},
        "options": [
            {"id": "spin", "uz": "Atrof aylanayotgandek, quloq shang'illaydi", "ru": "Всё вращается, шумит в ушах"},
            {"id": "dark", "uz": "Ko'z oldi qorong'ilashadi, yurak tez uradi", "ru": "Темнеет в глазах, сердце колотится"},
            {"id": "numb", "uz": "Gandiraklayman, qo'l-oyoq uvishadi", "ru": "Шатает, немеют руки или ноги"},
            {"id": "weak", "uz": "Holsizlik va isitma bilan", "ru": "Со слабостью и температурой"},
        ],
        "lik": {"nevrologiya": [.30, .15, .50, .05], "lor": [.75, .05, .15, .05],
                "kardiologiya": [.05, .85, .05, .05], "terapiya": [.10, .20, .10, .60]},
    },
    {
        "id": "headache_with",
        "text": {"uz": "Bosh og'rig'i bilan birga nima bor?", "ru": "Что сопровождает головную боль?"},
        "options": [
            {"id": "nausea", "uz": "Ko'ngil aynishi, yorug'likdan bezovtalik", "ru": "Тошнота, раздражает свет"},
            {"id": "nose", "uz": "Burun bitishi, peshona og'irligi", "ru": "Заложен нос, тяжесть во лбу"},
            {"id": "fever", "uz": "Isitma, umumiy holsizlik", "ru": "Температура, общая слабость"},
            {"id": "pressure", "uz": "Qon bosimi ko'tarilgan", "ru": "Повышено давление"},
        ],
        "lik": {"nevrologiya": [.65, .05, .15, .15], "lor": [.05, .80, .10, .05],
                "terapiya": [.10, .10, .70, .10], "kardiologiya": [.10, .03, .07, .80]},
    },
    {
        "id": "fever",
        "text": {"uz": "Harorat (isitma) bormi?", "ru": "Есть температура?"},
        "options": [{"id": "high", "uz": "Ha, 38 dan yuqori", "ru": "Да, выше 38"},
                    {"id": "low", "uz": "Ozgina", "ru": "Небольшая"},
                    {"id": "no", "uz": "Yo'q", "ru": "Нет"}],
        "lik": {"terapiya": [.55, .30, .15], "lor": [.40, .30, .30], "pediatriya": [.55, .25, .20],
                "gastroenterologiya": [.15, .15, .70], "nevrologiya": [.05, .10, .85], "kardiologiya": [.05, .10, .85],
                "dermatologiya": [.05, .10, .85], "travmatologiya": [.03, .07, .90],
                "ginekologiya_urologiya": [.15, .15, .70], "laboratoriya": [.10, .10, .80]},
    },
    {
        "id": "main_area",
        "text": {"uz": "Sizni ko'proq nima bezovta qilyapti?", "ru": "Что беспокоит больше всего?"},
        "options": [
            {"id": "ent", "uz": "Tomoq, quloq yoki burun", "ru": "Горло, ухо или нос"},
            {"id": "body", "uz": "Butun tanada holsizlik va og'riq", "ru": "Слабость и ломота во всём теле"},
            {"id": "cough", "uz": "Yo'tal va nafas", "ru": "Кашель и дыхание"},
        ],
        "lik": {"lor": [.80, .05, .15], "terapiya": [.15, .55, .30], "pediatriya": [.35, .30, .35]},
    },
    {
        "id": "who",
        "text": {"uz": "Murojaat kim uchun?", "ru": "Для кого обращение?"},
        "options": [{"id": "adult", "uz": "O'zim yoki boshqa katta odam uchun", "ru": "Для себя или другого взрослого"},
                    {"id": "child", "uz": "14 yoshgacha bola uchun", "ru": "Для ребёнка до 14 лет"}],
        "lik": {"pediatriya": [.02, .98], "*": [.95, .05]},
    },
    {
        "id": "skin",
        "text": {"uz": "Terida toshma yoki qichishish bormi?", "ru": "Есть сыпь или зуд на коже?"},
        "options": [{"id": "yes", "uz": "Ha", "ru": "Да"}, {"id": "no", "uz": "Yo'q", "ru": "Нет"}],
        "lik": {"dermatologiya": [.90, .10], "pediatriya": [.30, .70], "terapiya": [.10, .90], "lor": [.05, .95],
                "nevrologiya": [.05, .95], "travmatologiya": [.05, .95], "ginekologiya_urologiya": [.15, .85]},
    },
    {
        "id": "intent",
        "text": {"uz": "Sizga nima kerak?", "ru": "Что вам нужно?"},
        "options": [{"id": "doctor", "uz": "Shifokor ko'rigi — shikoyatim bor", "ru": "Приём врача — есть жалоба"},
                    {"id": "test", "uz": "Faqat tahlil yoki tekshiruv (qon, UZI, rentgen)",
                     "ru": "Только анализ или обследование (кровь, УЗИ, рентген)"}],
        "lik": {"laboratoriya": [.10, .90], "*": [.90, .10]},
    },
    {
        "id": "numb",
        "text": {"uz": "Qo'l, oyoq yoki yuzda uvishish yoki kuchsizlik bormi?",
                 "ru": "Есть онемение или слабость в руке, ноге или лице?"},
        "options": [{"id": "yes", "uz": "Ha", "ru": "Да"}, {"id": "no", "uz": "Yo'q", "ru": "Нет"}],
        "lik": {"nevrologiya": [.75, .25], "travmatologiya": [.20, .80], "kardiologiya": [.10, .90],
                "terapiya": [.15, .85]},
    },
]
_BY_ID = {q["id"]: q for q in QUESTIONS}
UNKNOWN = {"id": "unknown", "uz": "Bilmayman", "ru": "Не знаю"}


def _lik_matrix(q, labels):
    n = len(q["options"])
    default = q["lik"].get("*", [1.0 / n] * n)
    return np.array([q["lik"].get(l, default) for l in labels], dtype=float)   # (L, n)


def _entropy(p):
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def info_gain(P, q, labels):
    """Savol javobidan keyin kutilayotgan entropiya kamayishi (bit)."""
    M = _lik_matrix(q, labels)
    p_opt = P @ M                                   # har bir javob ehtimoli
    h_after = 0.0
    for o, po in enumerate(p_opt):
        if po > 0:
            h_after += po * _entropy(P * M[:, o] / po)
    return _entropy(P) - h_after


def select_question(P, labels, asked, min_gain):
    """Hali berilmagan savollar ichidan eng foydalisini tanlaydi (yoki None)."""
    best, best_gain = None, min_gain
    for q in QUESTIONS:
        if q["id"] in asked:
            continue
        g = info_gain(P, q, labels)
        if g > best_gain:
            best, best_gain = q, g
    return (best, best_gain) if best else (None, 0.0)


def update(P, labels, qid, option_id):
    """Bayes yangilanishi. 'Bilmayman' — o'zgarishsiz."""
    q = _BY_ID[qid]
    if option_id == UNKNOWN["id"]:
        return P
    idx = [o["id"] for o in q["options"]].index(option_id)
    post = P * _lik_matrix(q, labels)[:, idx]
    return post / post.sum()


def public(q):
    """Frontend'ga yuboriladigan ko'rinish."""
    return {"id": q["id"], "text": q["text"],
            "options": [{"id": o["id"], "text": {"uz": o["uz"], "ru": o["ru"]}} for o in q["options"] + [UNKNOWN]]}


def option_text(qid, option_id):
    q = _BY_ID[qid]
    for o in q["options"] + [UNKNOWN]:
        if o["id"] == option_id:
            return {"uz": o["uz"], "ru": o["ru"]}
    raise KeyError(option_id)


def validate():
    """Har bir ehtimollar qatori yig'indisi 1 ekanini tekshiradi."""
    for q in QUESTIONS:
        for dept, row in q["lik"].items():
            assert len(row) == len(q["options"]), (q["id"], dept)
            assert abs(sum(row) - 1) < 1e-6, (q["id"], dept, sum(row))


validate()

"""Bo'lim nomlari va bemorga ko'rsatiladigan backend matnlari (o'zbek / rus)."""

DEPARTMENTS = {
    "terapiya": {"uz": "Terapiya (umumiy tibbiyot)", "ru": "Терапия (общая медицина)"},
    "kardiologiya": {"uz": "Kardiologiya", "ru": "Кардиология"},
    "nevrologiya": {"uz": "Nevrologiya", "ru": "Неврология"},
    "gastroenterologiya": {"uz": "Gastroenterologiya", "ru": "Гастроэнтерология"},
    "lor": {"uz": "LOR (quloq, burun, tomoq)", "ru": "ЛОР (ухо, горло, нос)"},
    "dermatologiya": {"uz": "Dermatologiya va kosmetologiya", "ru": "Дерматология и косметология"},
    "pediatriya": {"uz": "Pediatriya", "ru": "Педиатрия"},
    "ginekologiya_urologiya": {"uz": "Ginekologiya va urologiya", "ru": "Гинекология и урология"},
    "travmatologiya": {"uz": "Travmatologiya va ortopediya", "ru": "Травматология и ортопедия"},
    "laboratoriya": {"uz": "Laboratoriya va diagnostika", "ru": "Лаборатория и диагностика"},
    "boshqa": {"uz": "Shifoxonamizda yo'q yo'nalish", "ru": "Направление, которого нет в нашей клинике"},
}

REASONS = {
    "explicit": {"uz": "Siz bo'limni o'zingiz ko'rsatdingiz.", "ru": "Вы сами указали отделение."},
    "model": {"uz": "Shikoyatingiz matni asosida tanlandi.", "ru": "Выбрано по тексту вашей жалобы."},
    "answers": {"uz": "Shikoyatingiz va javoblaringiz asosida tanlandi.",
                "ru": "Выбрано по жалобе и вашим ответам."},
    "low_conf": {"uz": "Tizim ishonch hosil qila olmadi — murojaatingizni operator ko'rib chiqadi.",
                 "ru": "Система не уверена — вашу заявку рассмотрит оператор."},
    "unknown": {"uz": "Bu murojaat tizimga notanish — operator ko'rib chiqadi.",
                "ru": "Такая жалоба системе незнакома — её рассмотрит оператор."},
    "urgent": {"uz": "Xavfli belgi aniqlandi — murojaatingiz darhol operatorga yuborildi.",
               "ru": "Обнаружен тревожный признак — заявка сразу передана оператору."},
    "other": {"uz": "Bu yo'nalish bo'yicha shifoxonamizda bo'lim yo'q.",
              "ru": "По этому направлению в нашей клинике нет отделения."},
    "not_medical": {"uz": "Iltimos, sog'lig'ingiz bilan bog'liq shikoyatni yozing.",
                    "ru": "Пожалуйста, опишите жалобу, связанную со здоровьем."},
}

CRISIS = {
    "uz": "Agar hozir o'zingizga zarar yetkazish xavfi bo'lsa, darhol 103 (tez tibbiy yordam) yoki 112 raqamiga "
          "qo'ng'iroq qiling yoki yaqin odamingizga ayting. Siz yolg'iz emassiz.",
    "ru": "Если сейчас есть риск, что вы причините себе вред, сразу позвоните 103 (скорая помощь) или 112 "
          "или скажите близкому человеку. Вы не одни.",
}


def dept_name(code: str) -> dict:
    return DEPARTMENTS.get(code, {"uz": code, "ru": code})


FLAGS_RU = {
    "O'z joniga qasd qilish xavfi — darhol yordam kerak": "Риск самоповреждения — нужна срочная помощь",
    "Ko'krak og'rig'i qo'l/jag'/kurakka tarqalmoqda (infarkt xavfi)": "Боль в груди отдаёт в руку/челюсть/лопатку (риск инфаркта)",
    "Og'riq chap qo'l/yelka yoki jag'ga tarqalmoqda (infarkt xavfi)": "Боль отдаёт в левую руку/плечо или челюсть (риск инфаркта)",
    "Infarkt shubhasi": "Подозрение на инфаркт",
    "Insult belgilari (yuz qiyshayishi, nutq buzilishi, bir tomon falaji)": "Признаки инсульта (перекос лица, нарушение речи, слабость с одной стороны)",
    "Hushdan ketish": "Потеря сознания",
    "Tutqanoq / talvasa": "Судороги / приступ",
    "Ichki qon ketish belgisi": "Признак внутреннего кровотечения",
    "Nafas olish jiddiy qiyinlashgan": "Серьёзное затруднение дыхания",
    "Homiladorlikda xavfli belgi": "Тревожный признак при беременности",
    "Bosh jarohatidan keyin qusish": "Рвота после травмы головы",
    "Juda yuqori harorat yoki bolada talvasa": "Очень высокая температура или судороги у ребёнка",
}


def flag_texts(flags):
    return [{"uz": f, "ru": FLAGS_RU.get(f, f)} for f in flags]

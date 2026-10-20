"""
Qoidalar qatlami (AI modelidan oldin/keyin ishlaydi). Kirish: textnorm.normalize() qilingan matn.

1. Aniq bo'lim nomi: bemor bitta bo'limni o'zi aytsa ("nevrologga yozilmoqchiman",
   "к кардиологу") — shu bo'lim tanlanadi.
2. Xavfli belgilar (red flags): yo'nalishni o'zgartirmaydi, lekin murojaatga
   "SHOSHILINCH" belgisi qo'yadi va sababini ko'rsatadi.
"""
import re

DEPT_PATTERNS = {
    "terapiya": r"terapevt|terapiya bo'lim|oilaviy (shifokor|vrach)|umumiy amaliyot|терапевт|семейн\w* врач|врач\w* общей практики",
    "kardiologiya": r"kardiolog|кардиолог",
    "nevrologiya": r"nevrolog|nevropatolog|asab shifokor|невролог|невропатолог",
    "gastroenterologiya": r"gastroenterolog|гастроэнтеролог",
    "lor": r"\blor\b|otorinolaringolog|quloq-burun-tomoq|\bлор\b|отоларинголог|оториноларинголог",
    "dermatologiya": r"dermatolog|kosmetolog|teri shifokor|дерматолог|косметолог",
    "pediatriya": r"pediatr|bolalar (shifokor|vrach|doktor)|педиатр|детск\w* врач",
    "ginekologiya_urologiya": r"ginekolog|\burolog|ayollar (shifokor|doktor)|гинеколог|\bуролог",
    "travmatologiya": r"travmatolog|ortoped|травматолог|ортопед",
    "laboratoriya": r"laboratoriya|лаборатори",
}
_DEPT = {k: re.compile(v) for k, v in DEPT_PATTERNS.items()}

SUICIDE_FLAG = "O'z joniga qasd qilish xavfi — darhol yordam kerak"
RED_FLAGS = [
    (SUICIDE_FLAG,
     r"o'zimni o'ldir|joniga qasd|o'z joni|yashagim kelmay|yashashni xohlamay|o'lgim kel|o'zimga zarar|"
     r"покончить с собой|суицид|не хочу жить|хочу умереть|причинить себе вред|убить себя"),
    ("Ko'krak og'rig'i qo'l/jag'/kurakka tarqalmoqda (infarkt xavfi)",
     r"(ko'krak|to'sh|yurak|груд|сердц)\w*.{0,40}(og'ri|sanch|siq|bos|бол|давит|давящ|жж|сжим|кол).{0,40}"
     r"(qo'l|jag'|yelka|kurak|рук|челюст|плеч|лопатк)"),
    ("Og'riq chap qo'l/yelka yoki jag'ga tarqalmoqda (infarkt xavfi)",
     r"(jag'|челюст).{0,30}(yelka|qo'l|плеч|рук)|(chap|лев\w*) (qo'l|yelka|руку|плечо).{0,30}(og'ri|tarqal|бол|отда)|"
     r"(og'ri|бол|отда)\w*.{0,30}(chap|лев\w*) (qo'l|yelka|руку|плечо)"),
    ("Infarkt shubhasi", r"infarkt bo'l|инфаркт(?! перен)|ko'krak.{0,40}sovuq ter|груд.{0,40}холодный пот"),
    ("Insult belgilari (yuz qiyshayishi, nutq buzilishi, bir tomon falaji)",
     r"yuz\w*.{0,30}(qiysha|uvish|karaxt)|лиц\w*.{0,30}(перекос|онемел)|перекосило|"
     r"gapir\w*.{0,15}qiyin|nutq\w* buzil|речь (спуталась|нарушил)|нарушилась речь|трудно говорить|insult|инсульт"),
    ("Hushdan ketish", r"hush\w*.{0,20}(yo'qot|ket)|сознани\w*.{0,10}(потер|терял)|потерял\w* сознани"),
    ("Tutqanoq / talvasa", r"tutqanoq|talvasa|судорог|эпилептическ\w* (приступ|припадок)|припадок"),
    ("Ichki qon ketish belgisi", r"qon\w*.{0,15}qus|qus\w*.{0,15}qon|рвот\w*.{0,15}кров|кров\w*.{0,15}рвот|"
     r"najas\w*.{0,15}qora|qora najas|черн\w* стул|чёрн\w* стул|стул\w* черн|стул\w* чёрн"),
    ("Nafas olish jiddiy qiyinlashgan", r"(?<!burnim bilan )(?<!burun bilan )nafas ol\w*.{0,15}(olmay|qiyin)|bo'g'ilib|"
     r"(?<!носом )не могу дышать|задыхаюсь|задыхается|удушь"),
    ("Homiladorlikda xavfli belgi", r"homilador\w*.{0,40}qon|беремен\w*.{0,40}кров|homila\w*.{0,30}sezmay|шевелени\w*.{0,30}(не|перестал)"),
    ("Bosh jarohatidan keyin qusish", r"(bosh\w*|голов\w*).{0,40}(urild|zarba|удар).{0,40}(qus|ko'ngl|рвот|тошн|вырвал)"),
    ("Juda yuqori harorat yoki bolada talvasa", r"\b(40|41)(,\d)?\b.{0,10}(harorat|isitma|температур)|(harorat|isitma|температур)\w*.{0,15}\b(40|41)\b"),
]
_FLAGS = [(name, re.compile(p)) for name, p in RED_FLAGS]


# "kardiologga borishdan oldin EKG", "перед кардиологом" — bo'lim nomi bor, lekin maqsad boshqa
_BEFORE = re.compile(r"(borishdan|kirishdan|uchrashishdan) oldin|\bперед\b|после (приёма|приема|визита)|"
                     r"yubordi|направил|направила|yo'llanma|направлени")


def explicit_department(text: str):
    """Matnda aynan bitta bo'lim nomi bo'lsa va u "...dan oldin" kontekstida bo'lmasa, shu bo'limni qaytaradi."""
    if _BEFORE.search(text):
        return None
    hits = [d for d, p in _DEPT.items() if p.search(text)]
    if len(hits) == 1:
        return hits[0]
    if not hits and other_specialty_explicit(text):
        return "boshqa"
    return None


_NOSE = re.compile(r"burn|burun|\bнос|ovoz|голос")
_TOOTH = re.compile(r"tish|milk|stomatolog|\bзуб|дёсн|десн|стоматолог")
_THROAT = re.compile(r"tomo|ovoz|hiqildoq|горл|гортан|голос|связк")


def red_flags(text: str):
    out = []
    for name, p in _FLAGS:
        if p.search(text):
            if name.startswith("Nafas") and _NOSE.search(text):   # burun bitishi / ovoz — shoshilinch emas
                continue
            if "infarkt" in name and _TOOTH.search(text):            # tish og'rig'i jag'ga beradi — infarkt emas
                continue
            if name.startswith("Insult") and _THROAT.search(text) and not re.search(r"yuz|лиц|insult|инсульт", text):
                continue                                          # tomoq og'rig'i tufayli gapirish qiyin
            out.append(name)
    return out


if __name__ == "__main__":
    from textnorm import normalize
    for s in ["Хочу записаться к неврологу", "kardiologga yozilmoqchiman, bosimim bor",
              "Боль отдаёт в челюсть и левое плечо", "yuzimning bir tomoni qiyshayib qoldi",
              "Бошимга урилдим, кейин қусдим", "bolamning harorati 40, talvasa bo'ldi",
              "tomog'im og'riyapti"]:
        t = normalize(s)
        print(f"{s:45s} dept={explicit_department(t)}  flags={red_flags(t)}")


# ---------------------------------------------------------------------------
# Shifoxonada YO'Q yo'nalishlar ("boshqa" sinfi uchun)
# ---------------------------------------------------------------------------
OTHER_EXPLICIT = {
    "stomatologiya": r"stomatolog|tish (shifokor|doktor|vrach)|стоматолог|зубн\w* врач",
    "oftalmologiya": r"oftalmolog|okulist|ko'z (shifokor|doktor|vrach)|офтальмолог|окулист|глазн\w* врач",
    "psixiatriya": r"psixiatr|psixolog|psixoterapevt|narkolog|психиатр|психолог|психотерапевт|нарколог",
    "onkologiya": r"onkolog|онколог|онкодиспансер",
    "endokrinologiya": r"endokrinolog|эндокринолог",
}
OTHER_HINTS = {
    "stomatologiya": r"tish|milk|\bзуб|дёсн|десн|пломб|коронк|брекет",
    "oftalmologiya": r"ko'z(?!ing)|ko'zoynak|глаз|зрени|очки|линз|катаракт",
    "onkologiya": r"saraton|o'sma|onko|rak\b|kimyo|рак\b|опухол|онко|хими|метастаз|лимфом|лейкоз",
    "endokrinologiya": r"qalqonsimon|buqoq|gormon|endokrin|щитовид|зоб|гормон|эндокрин|гипофиз|надпочеч",
    "psixiatriya": r"o'ldir|joniga|yashagim|умереть|не хочу жить|покончить|причинить себе|psix|ovozlar|kuzatayotgan|ichkilik|spirtli|narkot|giyohvand|qimor|голоса|следят|алког|нарко|пить\b|зависимост|психи",
}
_OTHER_EXPLICIT = {k: re.compile(v) for k, v in OTHER_EXPLICIT.items()}
_OTHER_HINTS = {k: re.compile(v) for k, v in OTHER_HINTS.items()}

OTHER_ADVICE = {
    "stomatologiya": {"uz": "stomatolog (tish shifokori)", "ru": "стоматолог"},
    "oftalmologiya": {"uz": "oftalmolog (ko'z shifokori)", "ru": "офтальмолог (окулист)"},
    "psixiatriya": {"uz": "psixiatr yoki psixoterapevt", "ru": "психиатр или психотерапевт"},
    "onkologiya": {"uz": "onkolog", "ru": "онколог"},
    "endokrinologiya": {"uz": "endokrinolog", "ru": "эндокринолог"},
}


def other_specialty_explicit(text: str):
    """Bemor shifoxonada yo'q mutaxassisni aniq aytgan bo'lsa ("stomatologga")."""
    hits = [k for k, p in _OTHER_EXPLICIT.items() if p.search(text)]
    return hits[0] if len(hits) == 1 else None


def other_subtype(text: str) -> str:
    """'boshqa' deb topilgan murojaat uchun taxminiy yo'nalish (bemorga maslahat berish uchun)."""
    exp = other_specialty_explicit(text)
    if exp:
        return exp
    for k, p in _OTHER_HINTS.items():
        if p.search(text):
            return k
    return "tibbiy_emas"

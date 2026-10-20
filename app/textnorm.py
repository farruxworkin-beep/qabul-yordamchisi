"""
Matnni normallashtirish (o'qitishda ham, veb-ilovada ham bir xil ishlatiladi).

1. Apostrof variantlari (ʻ ’ ‘ ` ʼ) -> '
2. O'zbekcha kirill matn -> lotin (rus matniga tegilmaydi)
3. Kichik harf, ortiqcha bo'shliqlar

Tilni oldindan bilish shart emas: o'zbekcha kirill matn maxsus harflar (ў қ ғ ҳ)
va o'zbekcha qo'shimcha/so'zlar orqali ruschadan ajratiladi.
"""
import re

_APOS = re.compile(r"[`ʻ’‘ʼ´]")
_CYR = re.compile(r"[а-яё]")
_UZ_LETTERS = re.compile(r"[ўқғҳ]")
# o'zbekcha kirill matnga xos so'z va qo'shimchalar
_UZ_MARKERS = re.compile(
    r"(кейин|юрак|ёзил|сидан|илиш|япти|япман|япсиз|моқчиман|ёшда|ёшдаман|ёш\b|кундан|ҳафтадан|бери|керак|бор\b|йўқ|"
    r"менга|мен\b|бўлди|бўлим|илтимос|ассалому|қабул|оғри|оғрия|шифокор|докторга|"
    r"ман\b|миз\b|дан\b|нинг\b|ни\b|га\b|да\b|ди\b|ти\b|лар|лари|ним\b|им\b|ингиз)")
_RU_MARKERS = re.compile(
    r"\b(и|в|не|на|что|у|меня|мне|с|по|при|после|уже|очень|когда|как|это|болит|болят|"
    r"хочу|нужно|можно|лет|года|день|ночью|сильно|ребёнка|ребенка)\b")

_C2L_MULTI = {"ш": "sh", "ч": "ch", "ё": "yo", "ю": "yu", "я": "ya", "ц": "ts", "ў": "o'", "ғ": "g'"}
_C2L = dict(zip("абвгдежзийклмнопрстуфхқҳъьыэщ",
                ["a", "b", "v", "g", "d", "e", "j", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s", "t",
                 "u", "f", "x", "q", "h", "'", "", "i", "e", "sh"]))


def is_uzbek_cyrillic(text: str) -> bool:
    t = text.lower()
    if not _CYR.search(t):
        return False
    if _UZ_LETTERS.search(t):
        return True
    uz = len(_UZ_MARKERS.findall(t))
    ru = len(_RU_MARKERS.findall(t))
    return uz > ru + 1


def cyr_to_lat(text: str) -> str:
    out = []
    for i, ch in enumerate(text):
        if ch in _C2L_MULTI:
            out.append(_C2L_MULTI[ch])
        elif ch == "е":                         # so'z boshida "ye"
            out.append("ye" if (i == 0 or not text[i - 1].isalpha()) else "e")
        else:
            out.append(_C2L.get(ch, ch))
    return "".join(out)


def normalize(text: str) -> str:
    t = _APOS.sub("'", str(text)).lower()
    if is_uzbek_cyrillic(t):
        t = cyr_to_lat(t)
    return re.sub(r"\s+", " ", t).strip()


if __name__ == "__main__":
    for s in ["Бошим қаттиқ оғрияпти", "Менга 30 ёш, тиззам шишди", "Сильно болит голова",
              "Qorin og‘rig‘i bor", "мен 47 ёшдаман, орқа мия билан муаммо бор дейишди"]:
        print(s, "->", normalize(s))

# Qabul yordamchisi — bemor murojaatini klinik yo'nalishga yo'naltirish (DL №35)

Bemor shikoyatini o'z so'zlari bilan (o'zbekcha lotin/kirill yoki ruscha) yozadi — tizim mos bo'limni
tavsiya qiladi, kerak bo'lsa aniqlashtiruvchi savol beradi, ishonch past yoki xavfli belgi bo'lsa
murojaatni operatorga yuboradi. **Tizim tashxis qo'ymaydi.**

## Murojaat yo'li

```
matn ─► normallashtirish (kirill→lotin, apostroflar)          app/textnorm.py
     ─► qoidalar: bo'lim nomi? xavfli belgi? shifoxonada yo'q?  app/rules.py
     ─► AI ensemble (E5-large + XLM-R + E5-base, og'irlikli)    app/predictor.py
     ─► [OOD: E5 masofasi — notanish murojaat]
     ─► qaror                                                   app/engine.py
          ├ ishonch ≥ 0.6           → bo'lim
          ├ "boshqa" sinfi          → shifoxonada yo'q yo'nalish + tavsiya (stomatolog, okulist…)
          ├ qisqa noaniq shikoyat   → albatta savol ("qornim og'riyapti", "болит в груди")
          ├ ishonch past            → aniqlashtiruvchi savol (≤3)  app/clarify.py
          │                            · savol — eng katta axborot yutug'i (entropiya) bo'yicha
          │                            · javob — Bayes formulasi bilan hisobga olinadi
          └ baribir past / xavfli    → operator navbati
```

## Sahifalar

| Manzil | Vazifasi |
|---|---|
| `/` | Bemor sahifasi (o'zbek / rus) |
| `/operator` | Operator paneli (parol): navbat, to'g'ri bo'limni tasdiqlash, CSV eksport |
| `/stats` | Statistika (operator sifatida kirgandan keyin) |
| `/docs` | API hujjatlari (FastAPI avtomatik) |

Operator tasdiqlagan murojaatlar (`/api/export.csv`) — keyingi o'qitish uchun **haqiqiy belgilangan ma'lumot**.

## Fayllar

```
app/
  main.py        FastAPI yo'llari, operator avtorizatsiyasi (imzolangan cookie)
  engine.py      qaror mantiqi (bazadan mustaqil)
  predictor.py   modellarni yuklash, ensemble, OOD masofasi
  clarify.py     savollar banki + axborot yutug'i + Bayes yangilanishi
  rules.py       bo'lim nomi, xavfli belgilar, shifoxonada yo'q yo'nalishlar
  textnorm.py    matn normallashtirish
  db.py          SQLite (murojaatlar, operator qarorlari, statistika)
  i18n.py        bo'lim nomlari, bemorga matnlar (uz/ru)
  config.py      sozlamalar (muhit o'zgaruvchilari)
static/          HTML/CSS/JS (frameworksiz)
fallback_model/  zaxira TF-IDF modeli (11 sinf) — katta modellar bo'lmasa ishlaydi
models/          ← Colab'dan yuklangan triage_models_vX shu yerga
evaluate.py      to'liq tizimni test to'plamida baholash
train_fallback.py zaxira modelni qayta o'qitish
tests/           avtomatik testlar (pytest)
```

## Ishga tushirish

### 1) Tez (zaxira TF-IDF modeli bilan)
```bash
pip install -r requirements.txt
OPERATOR_PASSWORD=parolingiz uvicorn app.main:app --port 8000
# brauzerda: http://localhost:8000
```

### 2) To'liq ensemble bilan
```bash
pip install -r requirements-full.txt
unzip triage_models_v5.zip            # triage_models/ papkasi chiqadi
TRIAGE_MODELS_DIR=triage_models OPERATOR_PASSWORD=parolingiz uvicorn app.main:app --port 8000
```
- Kerakli xotira: ~5–6 GB (3 ta transformer CPU'da). Bitta murojaat ~0.5–1.5 soniya.
- Birinchi ishga tushishda E5-base (OOD masofasi uchun) Hugging Face'dan avtomatik yuklanadi.
- `config.json` dagi `sklearn` versiyasi bilan o'rnatilgan versiya farq qilsa, TF-IDF a'zosi
  yuklanmasligi mumkin — tizim qolgan modellar bilan ishlayveradi (logda ogohlantirish chiqadi).
- v4 modellari (10 sinf) ham ishlaydi: "boshqa" sinfi o'rniga faqat qoidalar va ishonch chegarasi.

### 3) Tekshirish
```bash
python -m pytest -q                       # 12 ta test
python evaluate.py path/to/data_v5        # toza test va OOD testida to'liq tizim natijasi
```

### 4) Internetga joylash
**Doimiy havola (Render, bepul, zaxira TF-IDF):** GitHub repozitoriyasini Render'ga ulang — `render.yaml`
sozlamalarni o'zi beradi; `OPERATOR_PASSWORD` ni Render'da kiriting. Bepul tarif 15 daqiqa ishlatilmasa
uxlaydi — birinchi ochilish ~1 daqiqa.

**To'liq ensemble demo (Colab GPU + Cloudflare tunnel, bepul):** `colab_save_models.py` (bir marta —
modellarni Hugging Face'ga yopiq repozitoriyaga saqlaydi), keyin `colab_run_demo.py` — ilova GPU'da ishga
tushadi va `https://....trycloudflare.com` havolasi chiqadi (Colab ochiq turganda ishlaydi).

**Hugging Face Spaces (PRO obuna kerak — 2026-yildan Docker Space'lar bepul emas):**
Modellar Colab'da turgani uchun ularni kompyuterga yuklab olish shart emas.
1. huggingface.co'da ro'yxatdan o'ting → Settings → Access Tokens → **Write** token yarating.
2. `triage_v5.ipynb` oxirigi bo'limlari (9-bo'lim — saqlash) ishlab bo'lgach, yangi katak qo'shib,
   `colab_deploy.py` ichidagi kodni joylang va ishga tushiring.
3. So'ralganda: token, operator paroli va `triage-app.zip` faylini bering.
4. Katak: modellarni `user/triage-models` ga, ilovani `user/qabul-yordamchisi` Space'ga yuklaydi,
   kutubxona versiyalarini Colab bilan moslaydi, parolni Space secret sifatida saqlaydi.
5. Space 10–20 daqiqada quriladi; birinchi ishga tushishda modellar (~3 GB) yuklanadi — yana bir necha daqiqa.

Bepul Space: 2 vCPU, 16 GB xotira; bitta murojaat ~1–3 soniya. 48 soat ishlatilmasa "uxlaydi" —
birinchi ochilishda uyg'onishi uchun 1–2 daqiqa kutiladi. Ma'lumotlar bazasi (SQLite) Space qayta
ishga tushganda tozalanadi — demo uchun yetarli; doimiy saqlash uchun pullik "Persistent storage" kerak.

## Sozlamalar (muhit o'zgaruvchilari)

| O'zgaruvchi | Standart | Ma'nosi |
|---|---|---|
| `TRIAGE_MODELS_DIR` | `models` | ensemble modellari papkasi |
| `OPERATOR_PASSWORD` | `admin123` | operator paroli — **albatta o'zgartiring** |
| `TRIAGE_SECRET` | tasodifiy | cookie imzosi kaliti (qayta ishga tushganda saqlanishi uchun bering) |
| `TRIAGE_THRESHOLD` | 0.6 | avtomatik yo'naltirish ishonch chegarasi |
| `TRIAGE_MAX_QUESTIONS` | 3 | eng ko'p aniqlashtiruvchi savol |
| `TRIAGE_ANSWERED_THRESHOLD` | 0.45 | savollarga javobdan keyin yo'naltirish chegarasi (2-o'rindan farq ≥ 0.2) |
| `TRIAGE_DB` | `triage.db` | SQLite fayli |

## Zaxira model bilan natija (`evaluate.py`, data_v5)
- 10 bo'lim toza testi: qat'iy 93.3%, maqbul 95.5%; avtomatik yo'naltirilgan 91.8%, ulardagi aniqlik 97.8%
- OOD testi: begona murojaatlarning 89.8% i ushlandi; oddiy murojaatlarning 0.5% i xato "boshqa" deb topildi
- Bitta murojaat: ~6 ms

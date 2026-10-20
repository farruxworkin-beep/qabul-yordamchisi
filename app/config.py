"""Ilova sozlamalari (muhit o'zgaruvchilari orqali o'zgartiriladi)."""
import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Colab'dan yuklangan triage_models_vX ichidagilar shu papkaga ochiladi
MODELS_DIR = Path(os.getenv("TRIAGE_MODELS_DIR", BASE_DIR / "models"))
# Hugging Face model repozitoriyasi (masalan "user/triage-models"): models/ bo'sh bo'lsa, ishga tushishda yuklanadi
MODELS_REPO = os.getenv("TRIAGE_MODELS_REPO")
HF_TOKEN = os.getenv("HF_TOKEN")              # faqat repozitoriya yopiq (private) bo'lsa kerak
# Katta modellar bo'lmasa ishlaydigan yengil TF-IDF modeli
FALLBACK_DIR = BASE_DIR / "fallback_model"

DB_PATH = Path(os.getenv("TRIAGE_DB", BASE_DIR / "triage.db"))

OPERATOR_PASSWORD = os.getenv("OPERATOR_PASSWORD", "admin123")
SECRET_KEY = os.getenv("TRIAGE_SECRET") or secrets.token_hex(32)

# Ishonch chegarasi: bundan past bo'lsa — savol yoki operator
THRESHOLD = float(os.getenv("TRIAGE_THRESHOLD", "0.6"))
MAX_QUESTIONS = int(os.getenv("TRIAGE_MAX_QUESTIONS", "3"))
# Savol berishga arziydigan minimal axborot yutug'i (bit)
MIN_INFO_GAIN = float(os.getenv("TRIAGE_MIN_INFO_GAIN", "0.05"))

TORCH_THREADS = int(os.getenv("TORCH_THREADS", "4"))
# "cuda" — Colab GPU'da tezroq; standart "cpu"
DEVICE = os.getenv("TRIAGE_DEVICE", "cpu")

# Savollarga javob berilgandan keyin: yetakchi bo'lim ishonchi va ikkinchisidan farqi shu qiymatlardan katta bo'lsa yo'naltiriladi
ANSWERED_THRESHOLD = float(os.environ.get("TRIAGE_ANSWERED_THRESHOLD", 0.45))
ANSWERED_MARGIN = float(os.environ.get("TRIAGE_ANSWERED_MARGIN", 0.2))

# ===================================================================================
# Hugging Face Spaces'ga joylash — shu katakni triage_v5.ipynb OXIRIGA qo'ying
# (9-bo'lim "Saqlash" ishlab bo'lgandan keyin; triage_models/ papkasi tayyor bo'lishi kerak)
#
# Kerak: huggingface.co'da akkaunt va WRITE huquqli token
#        (Settings → Access Tokens → Create new token → Write)
# ===================================================================================
!pip -q install -U huggingface_hub
import os, sys, zipfile, getpass, secrets, platform, re, json
import sklearn, numpy, pandas, joblib, transformers, sentence_transformers, torch
from huggingface_hub import HfApi

HF_TOKEN = getpass.getpass("Hugging Face token (Write): ")
OPERATOR_PASSWORD = getpass.getpass("Operator paneli uchun parol o'ylab toping: ")
PRIVATE_MODELS = False        # True qilsangiz, modellar yopiq bo'ladi (Space'ga token secret sifatida beriladi)

api = HfApi(token=HF_TOKEN)
user = api.whoami()["name"]
MODELS_REPO = f"{user}/triage-models"
SPACE = f"{user}/qabul-yordamchisi"
print("Foydalanuvchi:", user)

# --- 1) Ilova kodi ------------------------------------------------------------------
if not os.path.exists("triage-app/app/main.py"):
    from google.colab import files
    print("triage-app.zip faylini tanlang")
    up = files.upload()
    zipfile.ZipFile(next(iter(up))).extractall(".")

# --- 2) Versiyalarni Colab bilan moslash (joblib modellari aynan shu versiyada ochiladi) ---
py = ".".join(platform.python_version_tuple()[:2])
open("triage-app/requirements.txt", "w").write(f"""fastapi==0.150.0
uvicorn==0.53.0
scikit-learn=={sklearn.__version__}
numpy=={numpy.__version__}
pandas=={pandas.__version__}
joblib=={joblib.__version__}
huggingface_hub
""")
open("triage-app/requirements-full.txt", "w").write(f"""-r requirements.txt
--extra-index-url https://download.pytorch.org/whl/cpu
torch=={torch.__version__.split('+')[0]}
transformers=={transformers.__version__}
sentence-transformers=={sentence_transformers.__version__}
sentencepiece
""")
df = open("triage-app/Dockerfile").read()
open("triage-app/Dockerfile", "w").write(re.sub(r"FROM python:[\d.]+-slim", f"FROM python:{py}-slim", df))
# zaxira modelni ham Colab'dagi sklearn bilan qayta o'qitamiz
!cd triage-app && python train_fallback.py ../data_v5

# --- 3) Space uchun README sarlavhasi ---------------------------------------------------
readme = open("triage-app/README.md").read()
if not readme.startswith("---"):
    open("triage-app/README.md", "w").write(
        "---\ntitle: Qabul yordamchisi\nemoji: 🏥\ncolorFrom: blue\ncolorTo: green\nsdk: docker\n"
        "app_port: 7860\nstartup_duration_timeout: 1h\npinned: false\n---\n\n" + readme)

# --- 4) Modellarni yuklash ---------------------------------------------------------------
api.create_repo(MODELS_REPO, repo_type="model", private=PRIVATE_MODELS, exist_ok=True)
api.upload_folder(folder_path="triage_models", repo_id=MODELS_REPO, repo_type="model",
                  commit_message="triage modellari (v5)")
print("Modellar:", f"https://huggingface.co/{MODELS_REPO}")

# --- 5) Space yaratish va sozlash ---------------------------------------------------------
api.create_repo(SPACE, repo_type="space", space_sdk="docker", exist_ok=True)
api.add_space_variable(SPACE, "TRIAGE_MODELS_REPO", MODELS_REPO)
api.add_space_secret(SPACE, "OPERATOR_PASSWORD", OPERATOR_PASSWORD)
api.add_space_secret(SPACE, "TRIAGE_SECRET", secrets.token_hex(32))
if PRIVATE_MODELS:
    api.add_space_secret(SPACE, "HF_TOKEN", HF_TOKEN)
api.upload_folder(folder_path="triage-app", repo_id=SPACE, repo_type="space",
                  ignore_patterns=["models/*", "*.db", "**/__pycache__/*", ".pytest_cache/*"],
                  commit_message="Qabul yordamchisi")

url = f"https://{user.lower().replace('_', '-').replace('.', '-')}-qabul-yordamchisi.hf.space"
print("\nTayyor! Space quriladi (10–20 daqiqa):", f"https://huggingface.co/spaces/{SPACE}")
print("Ilova manzili:", url)

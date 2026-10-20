# ===================================================================================
# 1-KATAK (bir marta): o'qitilgan modellarni Hugging Face'ga saqlash
# triage_v5.ipynb oxiriga qo'ying — 9-bo'lim (saqlash) tugagandan keyin.
# Model repozitoriyalari bepul; repozitoriya YOPIQ (private) bo'ladi.
# ===================================================================================
!pip -q install -U huggingface_hub
import getpass
from huggingface_hub import HfApi
api = HfApi(token=getpass.getpass("Hugging Face token (Write): "))
user = api.whoami()["name"]
MODELS_REPO = f"{user}/triage-models"
api.create_repo(MODELS_REPO, repo_type="model", private=True, exist_ok=True)
api.upload_folder(folder_path="triage_models", repo_id=MODELS_REPO, repo_type="model",
                  commit_message="triage modellari (v5)")
print("Saqlandi:", f"https://huggingface.co/{MODELS_REPO}")

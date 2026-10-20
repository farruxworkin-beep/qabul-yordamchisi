# ===================================================================================
# HAMMASI BITTA JOYDAN (Colab): triage-app.zip yuklangandan keyin ishga tushadi.
#   1) GitHub'ni yangilash (Render sayti ham yangilanadi)      — ixtiyoriy, token kerak
#   2) Modellarni Hugging Face'ga saqlash (keyingi sessiyalar uchun) — ixtiyoriy, token kerak
#   3) To'liq ensemble demo: GPU + ochiq havola (trycloudflare)
# Har bir tokenni o'tkazib yuborish uchun bo'sh qoldirib Enter bosing.
# ===================================================================================
import os, shutil, subprocess, getpass


# ---------- 1) GitHub (Render) ----------
get_ipython().run_cell(open("triage-app/colab_push_github.py", encoding="utf-8").read())

# ---------- 2) Hugging Face (modellar zaxirasi) ----------
if os.path.exists("triage_models/config.json"):
    hf = getpass.getpass("Hugging Face token (Write) — modellarni saqlash uchun (o'tkazish: Enter): ").strip()
    if hf:
        try:
            from huggingface_hub import HfApi
            api = HfApi(token=hf)
            repo = f"{api.whoami()['name']}/triage-models"
            api.create_repo(repo, repo_type="model", private=True, exist_ok=True)
            api.upload_folder(folder_path="triage_models", repo_id=repo, repo_type="model",
                              commit_message="triage modellari (v5)")
            print("✅ Modellar saqlandi (yopiq):", f"https://huggingface.co/{repo}")
        except Exception as e:
            print("⚠️ Hugging Face'ga saqlab bo'lmadi:", str(e)[:300])
    del hf

# ---------- 3) Demo ----------
get_ipython().run_cell(open("triage-app/colab_run_demo.py", encoding="utf-8").read())

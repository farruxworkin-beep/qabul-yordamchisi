# ===================================================================================
# HAMMASI BITTA JOYDAN (Colab): triage-app.zip yuklangandan keyin ishga tushadi.
#   1) GitHub'ni yangilash (Render sayti ham yangilanadi)      — ixtiyoriy, token kerak
#   2) Modellarni Hugging Face'ga saqlash (keyingi sessiyalar uchun) — ixtiyoriy, token kerak
#   3) To'liq ensemble demo: GPU + ochiq havola (trycloudflare)
# Har bir tokenni o'tkazib yuborish uchun bo'sh qoldirib Enter bosing.
# ===================================================================================
import os, shutil, subprocess, getpass

GITHUB_REPO = "farruxworkin-beep/qabul-yordamchisi"

# ---------- 1) GitHub (Render) ----------
gh = getpass.getpass("GitHub token — Render saytini yangilash uchun (o'tkazish: Enter): ").strip()
if gh:
    try:
        shutil.rmtree("gh_repo", ignore_errors=True)
        url = f"https://x-access-token:{gh}@github.com/{GITHUB_REPO}.git"
        subprocess.run(["git", "clone", "-q", url, "gh_repo"], check=True, capture_output=True)
        for item in os.listdir("gh_repo"):
            if item != ".git":
                p = os.path.join("gh_repo", item)
                shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
        shutil.copytree("triage-app", "gh_repo", dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("*.db", "__pycache__", "models"))
        g = lambda *a: subprocess.run(["git", "-C", "gh_repo", *a], check=True, capture_output=True)
        g("add", "-A")
        if subprocess.run(["git", "-C", "gh_repo", "diff", "--cached", "--quiet"]).returncode:
            g("-c", "user.name=farrux", "-c", "user.email=noreply@example.com",
              "commit", "-q", "-m", "Yangilanish: aniqlashtiruvchi savollar")
            g("push", "-q", "origin", "HEAD")
            print("✅ GitHub yangilandi — Render 3–5 daqiqada saytni qayta joylaydi.")
        else:
            print("✅ GitHub'da kod allaqachon yangi.")
    except subprocess.CalledProcessError as e:
        print("⚠️ GitHub'ga yuklab bo'lmadi:", (e.stderr or b"").decode().replace(gh, "***")[-300:])
    finally:
        shutil.rmtree("gh_repo", ignore_errors=True)
del gh

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

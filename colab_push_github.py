# GitHub'ni yangilash (Render sayti ham yangilanadi). colab_all_in_one.py va colab_update.py chaqiradi.
import os, shutil, subprocess, getpass
GITHUB_REPO = "farruxworkin-beep/qabul-yordamchisi"
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


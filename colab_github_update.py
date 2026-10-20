# ===================================================================================
# Kodni GitHub'da yangilash (Render avtomatik qayta joylaydi). Istalgan Colab katagida ishlaydi.
# So'raladi: GitHub token (yashirin kiritiladi) va yangi triage-app.zip fayli.
# ===================================================================================
REPO = "farruxworkin-beep/qabul-yordamchisi"
import getpass, os, shutil, subprocess, zipfile
from google.colab import files
tok = getpass.getpass("GitHub token: ")
print("triage-app.zip faylini tanlang:")
name = next(iter(files.upload()))
shutil.rmtree("upd", ignore_errors=True); shutil.rmtree("repo", ignore_errors=True)
zipfile.ZipFile(name).extractall("upd")
src = "upd/triage-app" if os.path.isdir("upd/triage-app") else "upd"
url = f"https://x-access-token:{tok}@github.com/{REPO}.git"
run = lambda *a, **k: subprocess.run(list(a), check=True, **k)
run("git", "clone", "-q", url, "repo")
for item in os.listdir("repo"):                      # .git dan boshqa hammasini yangisi bilan almashtiramiz
    if item != ".git":
        p = os.path.join("repo", item)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
shutil.copytree(src, "repo", dirs_exist_ok=True)
run("git", "-C", "repo", "add", "-A")
run("git", "-C", "repo", "-c", "user.name=farrux", "-c", "user.email=noreply@example.com",
    "commit", "-q", "-m", "Noaniq qisqa shikoyatlarga aniqlashtiruvchi savol")
run("git", "-C", "repo", "push", "-q", "origin", "HEAD")
shutil.rmtree("repo"); del tok
print("GitHub yangilandi. Render 3–5 daqiqada qayta joylaydi.")

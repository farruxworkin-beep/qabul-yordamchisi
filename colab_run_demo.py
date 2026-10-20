# ===================================================================================
# 2-KATAK: to'liq ensemble'ni Colab GPU'da ishga tushirish + ochiq havola (Cloudflare tunnel)
# Istalgan Colab'da ishlaydi (Runtime → T4 GPU tavsiya etiladi):
#   - triage_models/ papkasi bo'lsa, shuni ishlatadi; bo'lmasa Hugging Face'dan yuklaydi
#   - ilova kodi GitHub'dan olinadi
# Havola katak (va Colab sessiyasi) ishlab turgan paytda ishlaydi.
# ===================================================================================
GITHUB_REPO = "https://github.com/farruxworkin-beep/qabul-yordamchisi"   # o'zingiznikiga moslang

!pip -q install fastapi uvicorn huggingface_hub sentence-transformers
import os, re, time, subprocess, getpass, urllib.request

if not os.path.exists("triage-app/app/main.py"):
    !git clone -q {GITHUB_REPO} triage-app

if not os.path.exists("triage_models/config.json"):
    from huggingface_hub import HfApi, snapshot_download
    tok = getpass.getpass("Hugging Face token (Read yoki Write): ")
    user = HfApi(token=tok).whoami()["name"]
    snapshot_download(f"{user}/triage-models", local_dir="triage_models", token=tok)

if not os.path.exists("cloudflared"):
    !wget -q -O cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
    !chmod +x cloudflared

env = dict(os.environ,
           TRIAGE_MODELS_DIR=os.path.abspath("triage_models"),
           TRIAGE_DEVICE="cuda",
           TRIAGE_DB=os.path.abspath("triage_demo.db"),
           OPERATOR_PASSWORD=getpass.getpass("Operator paneli uchun parol: "))
for p in ("srv", "tun"):
    if p in globals():
        globals()[p].terminate()
srv = subprocess.Popen(["python", "-m", "uvicorn", "app.main:app", "--port", "8000"], cwd="triage-app",
                       env=env, stdout=open("server.log", "w"), stderr=subprocess.STDOUT)
print("Modellar yuklanmoqda (1–3 daqiqa)...")
for _ in range(300):
    try:
        info = urllib.request.urlopen("http://localhost:8000/api/info", timeout=2).read().decode()
        break
    except Exception:
        time.sleep(2)
        if srv.poll() is not None:
            print(open("server.log").read()[-3000:]); raise SystemExit("Server ishga tushmadi")
print("Server tayyor:", info[:300])

tun = subprocess.Popen(["./cloudflared", "tunnel", "--url", "http://localhost:8000", "--no-autoupdate"],
                       stdout=subprocess.DEVNULL, stderr=open("tunnel.log", "w"))
url = None
for _ in range(60):
    time.sleep(1)
    m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", open("tunnel.log").read())
    if m:
        url = m.group(0); break
print("\n==============================================")
print("Ilova:          ", url)
print("Operator paneli:", f"{url}/operator")
print("Statistika:     ", f"{url}/stats")
print("==============================================")
print("Havola Colab ochiq turganda ishlaydi. To'xtatish: srv.terminate(); tun.terminate()")

# ===================================================================================
# YANGILASH (demo ishlab turganda): yangi triage-app.zip -> GitHub/Render -> serverni qayta ishga tushirish.
# Demo havolasi O'ZGARMAYDI; modellar va operator paroli avvalgidek qoladi.
# ===================================================================================
import time, subprocess, urllib.request
get_ipython().run_cell(open("triage-app/colab_push_github.py", encoding="utf-8").read())
if "srv" not in globals() or "env" not in globals():
    print("Demo hali ishga tushmagan — 10-bo'lim katagini ishga tushiring.")
else:
    srv.terminate(); srv.wait()
    srv = subprocess.Popen(["python", "-m", "uvicorn", "app.main:app", "--port", "8000"], cwd="triage-app",
                           env=env, stdout=open("server.log", "w"), stderr=subprocess.STDOUT)
    print("Server qayta ishga tushmoqda...")
    for _ in range(300):
        try:
            urllib.request.urlopen("http://localhost:8000/api/info", timeout=2); break
        except Exception:
            time.sleep(2)
            if srv.poll() is not None:
                print(open("server.log").read()[-3000:]); raise SystemExit("Server ishga tushmadi")
    print("✅ Yangi kod ishlayapti. Havola o'sha:", globals().get("DEMO_URL", "(10-bo'limdagi havola)"))

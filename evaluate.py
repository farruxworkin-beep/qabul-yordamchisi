"""
Ilovaning to'liq qaror mantiqini (normallashtirish + qoidalar + model + OOD) test to'plamida baholaydi.
Colab'dagi natijani CPU'da qayta tekshirish uchun.

Ishlatish:  python evaluate.py path/to/data_v5
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from app import engine  # noqa: E402
from app.predictor import Predictor  # noqa: E402


def run(df, p):
    out = []
    for t in df.text:
        st = engine.new_state(t, p)
        out.append(engine.decide(st, p, allow_questions=False))
    return out


def main(data):
    p = Predictor()
    print("Rejim:", p.mode, p.weights)
    test = pd.read_csv(data / "test.csv"); test["alt"] = test.get("alt", pd.Series([""] * len(test))).fillna("")
    t0 = time.time(); res = run(test, p); dt = (time.time() - t0) / len(test)
    pred = np.array([r["department"] for r in res])
    status = np.array([r["status"] for r in res])
    strict = pred == test.label.values
    ok = np.array([s or d in a.split("|") for s, d, a in zip(strict, pred, test.alt)])
    routed = status == "routed"
    print(f"\n10 bo'lim testi ({len(test)}):  qat'iy={strict.mean():.3f}  maqbul={ok.mean():.3f}")
    print(f"  avtomatik yo'naltirildi={routed.mean():.3f}  ulardagi aniqlik (maqbul)={ok[routed].mean():.3f}")
    print(f"  operatorga={np.mean(status == 'operator'):.3f}  xato 'boshqa'={np.mean(np.isin(status, ['other', 'not_medical'])):.3f}")
    print(f"  bitta murojaatga o'rtacha vaqt: {dt * 1000:.0f} ms")

    f = data / "test_ood.csv"
    if f.exists():
        ood = pd.read_csv(f)
        st = np.array([r["status"] for r in run(ood, p)])
        caught = np.isin(st, ["other", "not_medical", "operator"])
        print(f"\nOOD testi ({len(ood)}): begona murojaat ushlandi={caught.mean():.3f}  "
              f"(boshqa/tibbiy emas={np.isin(st, ['other', 'not_medical']).mean():.3f})")
        ood["caught"] = caught
        print(ood.groupby("sub").caught.mean().round(2).to_dict())


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "data_v5"))

"""
Zaxira (fallback) model: TF-IDF + LinearSVM, 11 sinf. Katta modellar models/ da bo'lmasa ishlaydi.
Ishlatish: python train_fallback.py path/to/data_v5
"""
import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC

sys.path.insert(0, str(Path(__file__).parent))
from app.textnorm import normalize  # noqa: E402

data = Path(sys.argv[1] if len(sys.argv) > 1 else "data_v5")
df = pd.concat([pd.read_csv(data / "train.csv"), pd.read_csv(data / "val.csv")])
model = Pipeline([
    ("f", FeatureUnion([
        ("w", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
        ("c", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True))])),
    ("clf", CalibratedClassifierCV(LinearSVC(C=1.0), cv=3))])
model.fit(df.text.map(normalize), df.label)

out = Path(__file__).parent / "fallback_model"
out.mkdir(exist_ok=True)
joblib.dump(model, out / "tfidf.joblib", compress=3)
json.dump({"labels": sorted(df.label.unique()), "weights": {"TF-IDF": 1.0}, "threshold": 0.6,
           "note": "Zaxira model (TF-IDF). Haqiqiy ensemble uchun triage_models_vX ni models/ ga oching."},
          open(out / "config.json", "w"), indent=2, ensure_ascii=False)
print("saqlandi:", out, "sinflar:", len(df.label.unique()))

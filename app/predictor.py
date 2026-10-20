"""
Modellarni yuklash va ensemble ehtimollarini hisoblash.

models/ papkasida Colab'dan kelgan triage_models_vX bo'lsa — haqiqiy ensemble
(E5-large, XLM-R, E5-base va h.k., config.json'dagi og'irliklar bilan).
Bo'lmasa — fallback_model/ dagi yengil TF-IDF modeli ishlaydi.
"""
import json
import logging
from pathlib import Path

import numpy as np

from . import config

log = logging.getLogger("triage.predictor")


class Predictor:
    def __init__(self, models_dir: Path = config.MODELS_DIR, fallback_dir: Path = config.FALLBACK_DIR):
        self.members = {}          # nom -> funksiya(list[str]) -> np.ndarray (n, len(labels))
        self.weights = {}
        self.knn = None            # (embed_fn, index, tau, k)
        self.mode = "none"
        cfg_path = Path(models_dir) / "config.json"
        if not cfg_path.exists() and config.MODELS_REPO:
            self._download(Path(models_dir))
        if cfg_path.exists():
            self._load(Path(models_dir), json.loads(cfg_path.read_text(encoding="utf-8")))
            if self.members:
                self.mode = "ensemble"
        if not self.members:
            fb = Path(fallback_dir) / "config.json"
            if not fb.exists():
                raise RuntimeError("Model topilmadi: models/ yoki fallback_model/ kerak (README ga qarang)")
            self._load(Path(fallback_dir), json.loads(fb.read_text(encoding="utf-8")))
            self.mode = "fallback"
        total = sum(self.weights.values())
        self.weights = {k: v / total for k, v in self.weights.items()}
        log.info("Predictor rejimi=%s, modellar=%s", self.mode, self.weights)

    # ------------------------------------------------------------------ yuklash
    @staticmethod
    def _download(target: Path):
        """Hugging Face Hub'dan modellarni yuklab olish (Space'da birinchi ishga tushishda)."""
        try:
            from huggingface_hub import snapshot_download
            log.info("Modellar yuklanmoqda: %s -> %s", config.MODELS_REPO, target)
            snapshot_download(config.MODELS_REPO, local_dir=target, token=config.HF_TOKEN)
        except Exception as e:
            log.warning("Modellarni yuklab bo'lmadi (%s) — zaxira model ishlatiladi", e)

    def _load(self, d: Path, cfg: dict):
        self.cfg = cfg
        self.labels = cfg["labels"]
        self.threshold = cfg.get("threshold", config.THRESHOLD)
        weights = {k: v for k, v in cfg.get("weights", {}).items() if v > 0}
        for name, w in weights.items():
            try:
                fn = self._load_member(d, name, cfg)
            except Exception as e:                      # model yuklanmasa — qolganlari bilan ishlaymiz
                log.warning("%s yuklanmadi: %s", name, e)
                continue
            if fn is not None:
                self.members[name], self.weights[name] = fn, w
        if self.mode != "fallback" and cfg.get("ood_tau") and (d / "e5_index.npy").exists():
            try:
                self._load_knn(d, cfg)
            except Exception as e:
                log.warning("OOD masofa qatlami yuklanmadi: %s", e)

    def _reorder(self, classes):
        """Model sinflari tartibini config'dagi labels tartibiga keltiruvchi indekslar."""
        classes = list(classes)
        return [classes.index(l) if l in classes else None for l in self.labels]

    def _align(self, P, order):
        out = np.zeros((P.shape[0], len(self.labels)))
        for j, i in enumerate(order):
            if i is not None:
                out[:, j] = P[:, i]
        s = out.sum(1, keepdims=True)
        return out / np.where(s == 0, 1, s)

    def _load_member(self, d: Path, name: str, cfg: dict):
        import joblib
        if name == "TF-IDF":
            m = joblib.load(d / "tfidf.joblib")
            order = self._reorder(m.classes_)
            return lambda texts: self._align(m.predict_proba(texts), order)
        if name == "E5+LR":
            lr = joblib.load(d / "e5_logreg.joblib")
            embed = self._e5_embedder(cfg)
            order = self._reorder(lr.classes_)
            return lambda texts: self._align(lr.predict_proba(embed(texts)), order)
        sub = cfg.get("models", {}).get(name)
        if sub and (d / sub).exists():
            return self._load_transformer(d / sub, cfg.get("prefix", {}).get(name, ""))
        log.warning("%s uchun papka topilmadi", name)
        return None

    def _load_transformer(self, path: Path, prefix: str):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        torch.set_num_threads(config.TORCH_THREADS)
        tok = AutoTokenizer.from_pretrained(path)
        dev = config.DEVICE if (config.DEVICE != "cuda" or torch.cuda.is_available()) else "cpu"
        model = AutoModelForSequenceClassification.from_pretrained(
            path, torch_dtype=torch.float16 if dev == "cuda" else torch.float32).to(dev).eval()
        order = self._reorder([model.config.id2label[i] for i in range(model.config.num_labels)])

        def predict(texts):
            with torch.no_grad():
                enc = tok([prefix + t for t in texts], padding=True, truncation=True,
                          max_length=128, return_tensors="pt").to(dev)
                P = torch.softmax(model(**enc).logits.float(), -1).cpu().numpy()
            return self._align(P, order)
        return predict

    _e5 = None

    def _e5_embedder(self, cfg):
        if Predictor._e5 is None:
            from sentence_transformers import SentenceTransformer
            dev = config.DEVICE
            try:
                import torch
                if dev == "cuda" and not torch.cuda.is_available():
                    dev = "cpu"
            except ImportError:
                dev = "cpu"
            Predictor._e5 = SentenceTransformer(cfg.get("e5_embed_model", "intfloat/multilingual-e5-base"), device=dev)
        e5 = Predictor._e5
        return lambda texts: e5.encode(["query: " + t for t in texts], normalize_embeddings=True)

    def _load_knn(self, d: Path, cfg: dict):
        index = np.load(d / "e5_index.npy").astype(np.float32)
        self.knn = (self._e5_embedder(cfg), index, float(cfg["ood_tau"]), int(cfg.get("ood_k", 5)))

    # ------------------------------------------------------------------ bashorat
    def predict(self, norm_texts):
        """Normallashtirilgan matnlar -> (n, len(labels)) ehtimollar."""
        P = sum(w * self.members[n](norm_texts) for n, w in self.weights.items())
        return np.asarray(P)

    def ood_similarity(self, norm_texts):
        """Murojaat o'qitish misollariga qanchalik yaqin (kNN kosinus). Qatlam yo'q bo'lsa None."""
        if self.knn is None:
            return None
        embed, index, _, k = self.knn
        S = embed(norm_texts) @ index.T
        return np.sort(S, axis=1)[:, -k:].mean(1)

    @property
    def ood_tau(self):
        return self.knn[2] if self.knn else None

    def info(self):
        return {"mode": self.mode, "labels": self.labels, "weights": self.weights,
                "threshold": self.threshold, "ood_distance": self.knn is not None,
                "test": self.cfg.get("test")}

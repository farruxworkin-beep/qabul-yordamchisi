"""
Qaror mantiqi (bazadan mustaqil — evaluate.py ham shuni ishlatadi).

  matn → normallashtirish → qoidalar → AI ensemble → [OOD tekshiruvi] → qaror
  qaror: routed (bo'lim) | question (savol) | operator | other (shifoxonada yo'q) | not_medical
"""
import numpy as np

from . import clarify, config
from .i18n import CRISIS, REASONS, dept_name, flag_texts
from .rules import SUICIDE_FLAG, explicit_department, other_subtype, red_flags, OTHER_ADVICE
from .textnorm import normalize


def new_state(text, predictor):
    norm = normalize(text)
    flags = red_flags(norm)
    state = {"text": text, "norm": norm, "flags": flags, "asked": [], "answers": [],
             "explicit": explicit_department(norm), "ood_sim": None}
    if len(norm.replace(" ", "")) < 3:
        state["P"] = None
        return state
    state["P"] = predictor.predict([norm])[0].tolist()
    sim = predictor.ood_similarity([norm])
    if sim is not None:
        state["ood_sim"] = float(sim[0])
    return state


def apply_answer(state, labels, qid, option_id):
    P = np.array(state["P"])
    state["P"] = clarify.update(P, labels, qid, option_id).tolist()
    state["answers"].append({"q": qid, "a": option_id})
    return state


def decide(state, predictor, allow_questions=True):
    labels = predictor.labels
    thr = predictor.threshold
    flags = state["flags"]
    urgent = bool(flags)
    crisis = SUICIDE_FLAG in flags
    res = {"urgent": urgent, "flags": flags, "flags_text": flag_texts(flags), "crisis": CRISIS if crisis else None,
           "question": None, "other": None, "top": [], "steps": []}

    if state["P"] is None:
        return {**res, "status": "not_medical", "department": None, "confidence": 0.0,
                "reason": REASONS["not_medical"]}

    P = np.array(state["P"])
    order = np.argsort(-P)
    res["top"] = [{"dept": labels[i], "name": dept_name(labels[i]), "p": round(float(P[i]), 3)}
                  for k, i in enumerate(order[:3]) if k == 0 or P[i] >= 0.02]
    best, conf = labels[order[0]], float(P[order[0]])
    res.update(department=best, confidence=round(conf, 3))
    res["steps"].append({"step": "model", "dept": best, "p": round(conf, 3)})

    def other(sub, reason_key="other"):
        adv = OTHER_ADVICE.get(sub)
        res["other"] = {"subtype": sub, "advice": adv}
        status = "not_medical" if sub == "tibbiy_emas" and not urgent else "other"
        return {**res, "status": status, "department": "boshqa", "reason": REASONS[
            "not_medical" if status == "not_medical" else reason_key]}

    # 1) bemor bo'limni o'zi aytgan
    exp = state.get("explicit")
    if exp == "boshqa":
        return other(other_subtype(state["norm"]))
    if exp:
        res["steps"].append({"step": "explicit", "dept": exp})
        return {**res, "status": "routed", "department": exp, "confidence": 1.0, "reason": REASONS["explicit"]}

    # 2) o'z joniga qasd qilish xavfi — har doim operatorga, inqiroz matni bilan
    if crisis:
        return {**res, "status": "operator", "reason": REASONS["urgent"]}

    # 3a) qisqa va noaniq shikoyat ("qornim og'riyapti") — mavzu aniq tibbiy, lekin bo'lim noaniq:
    #     OOD/"boshqa" tekshiruvidan oldin, model ishonchli bo'lsa ham bir marta aniqlashtiramiz
    if allow_questions and not urgent and not state["asked"]:
        cands, depts = clarify.vague_candidates(state["norm"])
        if cands:
            Pt = clarify.temper(P, labels, depts)
            scored = [(clarify.info_gain(Pt, clarify._BY_ID[q], labels), q) for q in cands]
            gain, qid = max(scored)
            if gain > config.MIN_INFO_GAIN:
                state["P"] = Pt.tolist()
                state["cands"] = cands
                state["asked"].append(qid)
                res["steps"].append({"step": "vague", "q": qid, "gain": round(gain, 3)})
                return {**res, "status": "question", "question": clarify.public(clarify._BY_ID[qid]), "reason": None}

    # 3) model "boshqa" dedi
    if best == "boshqa":
        return other(other_subtype(state["norm"]))

    # 4) notanish murojaat (E5 masofasi) — faqat model ham juda ishonchli bo'lmasa
    tau = predictor.ood_tau
    if tau is not None and state.get("ood_sim") is not None and state["ood_sim"] < tau and conf < 0.9 \
            and not state["answers"]:
        res["steps"].append({"step": "ood", "sim": round(state["ood_sim"], 3), "tau": round(tau, 3)})
        return {**res, "status": "operator", "reason": REASONS["unknown"]}

    # 5) ishonchli (bemor savollarga javob bergan va bitta bo'lim aniq oldinda bo'lsa — biroz pastroq chegara)
    second = float(P[order[1]]) if len(order) > 1 else 0.0
    answered_clear = bool(state["answers"]) and conf >= config.ANSWERED_THRESHOLD and conf - second >= config.ANSWERED_MARGIN
    if conf >= thr or answered_clear:
        return {**res, "status": "routed", "reason": REASONS["answers" if state["answers"] else "model"]}

    # 6) xavfli belgi bor, lekin bo'lim aniq emas — vaqt yo'qotmaymiz
    if urgent:
        return {**res, "status": "operator", "reason": REASONS["urgent"]}

    # 7) aniqlashtiruvchi savol
    if allow_questions and len(state["asked"]) < config.MAX_QUESTIONS:
        q, gain = clarify.select_question(P, labels, state["asked"], config.MIN_INFO_GAIN, state.get("cands"))
        if q is None and state.get("cands"):          # mavzu savollari tugadi — umumiy savollar banki
            q, gain = clarify.select_question(P, labels, state["asked"], config.MIN_INFO_GAIN)
        if q is not None:
            state["asked"].append(q["id"])
            res["steps"].append({"step": "question", "q": q["id"], "gain": round(gain, 3)})
            return {**res, "status": "question", "question": clarify.public(q), "reason": None}

    return {**res, "status": "operator", "reason": REASONS["low_conf"]}

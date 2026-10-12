#!/usr/bin/env python3
"""Buat webdata.js untuk aplikasi kartu di browser.

    python tools/build_web.py

Data tetap bersumber dari data/*.json. Berkas hasilnya dimuat lewat tag
<script>, bukan fetch(), supaya aplikasi jalan baik di GitHub Pages maupun
saat index.html dibuka langsung dari berkas (file://) tanpa masalah CORS.

Teks Kiril ditulis sebagai escape \\uXXXX (ASCII murni) supaya tidak bergantung
pada charset yang dikirim peladen.

Semua bentuk tanpa tanda tekanan, alih huruf, dan pendekatan lafal dihitung di
sini memakai rusdrill/cyrillic.py dan rusdrill/translit.py, sehingga logika
tekanan tidak perlu ditulis ulang dalam JavaScript dan tetap satu sumber
dengan yang dipakai quiz.py.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rusdrill import dataio  # noqa: E402
from rusdrill.cyrillic import (  # noqa: E402
    pronounce,
    pronounce_text,
    strip_stress,
    strip_stress_and_yo,
)
from rusdrill.questions import (  # noqa: E402
    render_item,
    render_level,
    target_word,
    vocab_detail,
)
from rusdrill.translit import translit  # noqa: E402

ROOT = dataio.ROOT
OUT = os.path.join(ROOT, "webdata.js")


def _ru(text: str) -> dict:
    """Satu teks Kiril beserta semua bentuk turunannya."""
    return {
        "ru": text,
        "bare": strip_stress(text),
        "bareNoYo": strip_stress_and_yo(text),
        "tr": translit(text),
        "lafal": pronounce_text(text),
    }


def build_alfabet() -> list[dict]:
    out = []
    for e in dataio.letters():
        out.append({
            "id": e["id"],
            "kind": "huruf",
            "face": "%s %s" % (e["upper"], e["lower"]),
            "upper": e["upper"],
            "lower": e["lower"],
            "name": e["name"],
            "nameTr": translit(e["name"]),
            "sound": e["sound"],
            "translit": e["translit"],
            "type": e["type"],
            "cat": e["group"],
            "catLabel": dataio.GROUP_LABEL.get(e["group"], e["group"]),
            "stage": e["stage"],
            "exRu": e["example"]["ru"],
            "exTr": translit(e["example"]["ru"]),
            "exLafal": pronounce_text(e["example"]["ru"]),
            "exGloss": e["example"]["gloss"],
            "note": e["note"],
        })
    for i in dataio.letter_items():
        out.append({
            "id": i["id"],
            "kind": "soal",
            "cat": "soal",
            "catLabel": "Soal huruf",
            "stage": i["stage"],
            "prompt": i["prompt"],
            "promptRu": i.get("prompt_ru") or "",
            "optionsLang": i["options_lang"],
            "options": i["options"],
            "answer": i["answer"],
            "explain": i.get("explain") or "",
        })
    return out


def build_kosakata() -> list[dict]:
    out = []
    for e in dataio.vocab_entries():
        row = {
            "id": e["id"],
            "gloss": e["gloss"],
            "alt": e.get("alt") or [],
            "detail": vocab_detail(e),
            "pos": dataio.POS_LABEL.get(e["pos"], e["pos"]),
            "root": (e.get("root") or "") and (e["root"] + "-"),
            "cat": e["cat"],
            "catLabel": dataio.CAT_LABEL.get(e["cat"], e["cat"]),
            "stage": e["stage"],
            "note": e.get("note") or "",
            "exRu": e["example"]["ru"],
            "exBare": strip_stress(e["example"]["ru"]),
            "exTr": translit(e["example"]["ru"]),
            "exLafal": pronounce_text(e["example"]["ru"]),
            "exGloss": e["example"]["gloss"],
        }
        row.update(_ru(e["ru"]))
        out.append(row)
    return out


def build_tatabahasa() -> list[dict]:
    out = []
    for t in dataio.grammar_topics():
        for item in t["items"]:
            out.append({
                "id": item["id"],
                "cat": t["id"],
                "catLabel": t["title"],
                "stage": t["stage"],
                "prompt": item["prompt"],
                "promptRu": item.get("prompt_ru") or "",
                "promptTr": translit(item.get("prompt_ru") or ""),
                "optionsLang": item["options_lang"],
                "options": item["options"],
                "answer": item["answer"],
                "explain": item.get("explain") or "",
            })
    for item in dataio.falsefriend_items():
        out.append({
            "id": item["id"],
            "cat": "palsu",
            "catLabel": "Teman palsu",
            "stage": item["stage"],
            "prompt": item["prompt"],
            "promptRu": item.get("prompt_ru") or "",
            "promptTr": translit(item.get("prompt_ru") or ""),
            "optionsLang": item["options_lang"],
            "options": item["options"],
            "answer": item["answer"],
            "explain": item.get("explain") or "",
        })
    return out


def build_topik() -> list[dict]:
    return [
        {
            "id": t["id"],
            "title": t["title"],
            "stage": t["stage"],
            "explanation": t["explanation"],
            "caveats": t["caveats"],
            "examples": [
                {"ru": x["ru"], "tr": translit(x["ru"]),
                 "lafal": pronounce_text(x["ru"]), "gloss": x["gloss"]}
                for x in t["examples"]
            ],
        }
        for t in dataio.grammar_topics()
    ]


def build_akar() -> list[dict]:
    out = []
    for fam in dataio.root_families():
        anggota = [m["ru"] for m in fam["members"]]
        for m in fam["members"]:
            row = {
                "id": "%s-%s" % (fam["id"], strip_stress(m["ru"])),
                "gloss": m["gloss"],
                "pattern": m["pattern"],
                "root": fam["root"] + "-",
                "rootMeaning": fam["meaning"],
                "variants": [v + "-" for v in (fam.get("variants") or [])],
                "cat": fam["id"],
                "catLabel": fam["root"] + "-",
                "stage": fam["stage"],
                "siblings": [strip_stress(a) for a in anggota if a != m["ru"]],
                "note": fam.get("note") or "",
            }
            row.update(_ru(m["ru"]))
            out.append(row)
    return out


def build_afiks() -> list[dict]:
    return [
        {
            "id": p["id"],
            "affix": p["affix"],
            "type": p["type"],
            "function": p["function"],
            "stage": p["stage"],
            "examples": [
                {"ru": x["ru"], "tr": translit(x["ru"]), "lafal": pronounce(x["ru"]),
                 "gloss": x["gloss"], "root": x["root"] + "-"}
                for x in p["examples"]
            ],
            "note": p.get("note") or "",
        }
        for p in dataio.root_patterns()
    ]


def build_baca() -> list[dict]:
    out = []
    for p in dataio.reading_passages():
        keep = set(p.get("keep") or [])
        out.append({
            "id": p["id"],
            "kind": "teks",
            "stage": p["stage"],
            "level": p["level"],
            "cat": "level%d" % p["level"],
            "catLabel": "Level %d" % p["level"],
            "l1": p["ru"],
            "l2": render_level(p["ru"], 2, keep=keep),
            "l3": render_level(p["ru"], 3),
            "l3NoYo": render_level(p["ru"], 3, yo=False),
            "tr": translit(p["ru"]),
            "lafal": pronounce_text(p["ru"]),
            "gloss": p["gloss"],
        })
    for i in dataio.reading_items():
        row = {
            "id": i["id"],
            "kind": "soal",
            "type": i["type"],
            "stage": i["stage"],
            "level": i["level"],
            "cat": "level%d" % i["level"],
            "catLabel": "Level %d" % i["level"],
            "l1": i["full_ru"],
            "l3": render_level(i["full_ru"], 3),
            "tr": translit(i["full_ru"]),
            "lafal": pronounce_text(i["full_ru"]),
            "gloss": i["gloss"],
            "options": i["options"],
            "optionsLang": i["options_lang"],
            "answer": i["answer"],
            "optionGlosses": i.get("option_glosses") or [],
            "explain": i.get("explain") or "",
            "prompt": i.get("prompt") or "",
        }
        target = i.get("target")
        if i["type"] == "stress_choice" and target is not None:
            row["shown"] = render_item(i["full_ru"], i["level"], target)
            row["targetBare"] = strip_stress(target_word(i["full_ru"], target))
        elif i["type"] == "pronounce_choice":
            row["shown"] = i["full_ru"]
            row["targetBare"] = ""
        else:
            row["shown"] = render_item(i["full_ru"], i["level"], None)
            row["targetBare"] = ""
        out.append(row)
    return out


def build_palsu() -> list[dict]:
    out = []
    for e in dataio.falsefriend_entries():
        row = {
            "id": e["id"],
            "gloss": e["gloss"],
            "mistaken": e["mistaken"],
            "correct": e.get("correct") or "",
            "correctTr": translit(e.get("correct") or ""),
            "kind": e["kind"],
            "cat": e["kind"],
            "catLabel": {"teman palsu": "Teman palsu", "serapan": "Kata serapan",
                         "gender": "Jebakan gender"}.get(e["kind"], e["kind"]),
            "stage": e["stage"],
            "note": e["note"],
        }
        row.update(_ru(e["ru"]))
        out.append(row)
    return out


def build_catatan() -> dict:
    d = dataio.load("falsefriends")
    r = dataio.load("reading")
    return {
        "palsu": d["catatan_penting"],
        "pemakaian": d["usage_notes"],
        "baca": r["catatan_penting"],
        "level": r["levels"],
        "akar": dataio.load("roots")["catatan_penting"],
        "grup": dataio.load("alphabet")["groups"],
    }


def main() -> int:
    data = {
        "alfabet": build_alfabet(),
        "kosakata": build_kosakata(),
        "tatabahasa": build_tatabahasa(),
        "topik": build_topik(),
        "akar": build_akar(),
        "afiks": build_afiks(),
        "baca": build_baca(),
        "palsu": build_palsu(),
        "catatan": build_catatan(),
    }
    data["meta"] = {k: len(v) for k, v in data.items() if isinstance(v, list)}

    body = json.dumps(data, ensure_ascii=True, separators=(",", ":"), sort_keys=False)
    teks = (
        "/* Dibuat otomatis oleh tools/build_web.py dari data/*.json.\n"
        "   JANGAN disunting langsung; sunting datanya lalu jalankan ulang skripnya. */\n"
        '"use strict";\n'
        "const RUS_DATA = " + body + ";\n"
    )
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(teks)
    kb = len(teks.encode("utf-8")) / 1024
    print("  webdata.js  (%.0f KB)" % kb)
    for k, n in data["meta"].items():
        print("    %-12s %4d" % (k, n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

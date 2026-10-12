#!/usr/bin/env python3
"""Buat ulang ekspor CSV dari data/*.json.

Hasilnya:
  data/csv/*.csv   tabel mentah untuk dibaca di penyunting lembar kerja
  anki/*.csv       berkas impor untuk Anki (tanpa baris judul)

Berkas JSON di data/ adalah satu-satunya sumber data. Jangan menyunting hasil
ekspor; sunting JSON-nya lalu jalankan ulang skrip ini.

    python tools/build_exports.py
"""

from __future__ import annotations

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rusdrill import dataio  # noqa: E402
from rusdrill.cyrillic import pronounce_text, strip_stress  # noqa: E402
from rusdrill.questions import render_item, target_word, vocab_detail  # noqa: E402
from rusdrill.translit import translit  # noqa: E402

ROOT = dataio.ROOT
CSV_DIR = os.path.join(ROOT, "data", "csv")
ANKI_DIR = os.path.join(ROOT, "anki")

#: Baris pengarah untuk Anki 2.1.55 ke atas. Versi Anki yang lebih tua tidak
#: mengenalinya; hapus baris-baris ini bila impor gagal (lihat anki/README.md).
ANKI_DIRECTIVES = ["#separator:Comma", "#html:false"]


def _write_csv(path: str, header: list[str], rows: list[list[str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        if header:
            w.writerow(header)
        w.writerows(rows)
    print("  %s  (%d baris)" % (os.path.relpath(path, ROOT), len(rows)))


def _write_anki(path: str, rows: list[list[str]], tags_column: int) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        for line in ANKI_DIRECTIVES:
            f.write(line + "\n")
        f.write("#tags column:%d\n" % tags_column)
        w = csv.writer(f, lineterminator="\n", quoting=csv.QUOTE_ALL)
        w.writerows(rows)
    print("  %s  (%d kartu)" % (os.path.relpath(path, ROOT), len(rows)))


def _s(value: object) -> str:
    """Ubah nilai menjadi teks; None dan daftar kosong menjadi string kosong."""
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join(str(v) for v in value)
    if isinstance(value, dict):
        return "; ".join("%s: %s" % (k, v) for k, v in value.items())
    return str(value)


# ---------------------------------------------------------------- data/csv ---

def export_alphabet_csv() -> None:
    rows = [
        [e["id"], e["upper"], e["lower"], e["name"], e["translit"], e["sound"],
         e["type"], e["group"], str(e["stage"]), e["example"]["ru"],
         pronounce_text(e["example"]["ru"]), e["example"]["gloss"], e["note"]]
        for e in dataio.letters()
    ]
    _write_csv(
        os.path.join(CSV_DIR, "alphabet.csv"),
        ["id", "upper", "lower", "name", "translit", "sound", "type", "group",
         "stage", "example_ru", "example_lafal", "example_gloss", "note"],
        rows,
    )


def export_vocab_csv() -> None:
    header = [
        "id", "ru", "bare", "translit", "lafal", "gloss", "alt", "pos", "gender",
        "plural", "aspect", "pair", "conj", "forms", "root", "example_ru",
        "example_gloss", "cat", "stage", "note",
    ]
    rows = [
        [
            e["id"], e["ru"], strip_stress(e["ru"]), translit(e["ru"]),
            pronounce_text(e["ru"]), e["gloss"], _s(e.get("alt")), e["pos"],
            _s(e.get("gender")), _s(e.get("plural")), _s(e.get("aspect")),
            _s(e.get("pair")), _s(e.get("conj")), _s(e.get("forms")),
            _s(e.get("root")), e["example"]["ru"], e["example"]["gloss"],
            e["cat"], str(e["stage"]), _s(e.get("note")),
        ]
        for e in dataio.vocab_entries()
    ]
    _write_csv(os.path.join(CSV_DIR, "vocab.csv"), header, rows)


def export_grammar_csv() -> None:
    _write_csv(
        os.path.join(CSV_DIR, "grammar_topics.csv"),
        ["id", "stage", "title", "explanation", "caveats", "examples"],
        [
            [t["id"], str(t["stage"]), t["title"], t["explanation"],
             " | ".join(t.get("caveats") or []),
             " | ".join("%s = %s" % (x["ru"], x["gloss"]) for x in t["examples"])]
            for t in dataio.grammar_topics()
        ],
    )
    _write_csv(
        os.path.join(CSV_DIR, "grammar_items.csv"),
        ["id", "topic_id", "stage", "type", "prompt", "prompt_ru", "options_lang",
         "options", "answer", "answer_text", "explain"],
        [
            [i["id"], i["topic_id"], str(i["stage"]), i["type"], i["prompt"],
             _s(i.get("prompt_ru")), i["options_lang"], " | ".join(i["options"]),
             str(i["answer"]), i["options"][i["answer"]], _s(i.get("explain"))]
            for i in dataio.grammar_items()
        ],
    )


def export_roots_csv() -> None:
    rows = []
    for fam in dataio.root_families():
        for m in fam["members"]:
            rows.append([
                fam["id"], fam["root"], _s(fam.get("variants")), fam["meaning"],
                str(fam["stage"]), m["ru"], translit(m["ru"]), pronounce_text(m["ru"]),
                m["gloss"], m["pattern"], _s(fam.get("note")),
            ])
    _write_csv(
        os.path.join(CSV_DIR, "roots_families.csv"),
        ["family_id", "root", "variants", "root_meaning", "stage", "ru", "translit",
         "lafal", "gloss", "pattern", "family_note"],
        rows,
    )
    _write_csv(
        os.path.join(CSV_DIR, "roots_patterns.csv"),
        ["id", "affix", "type", "function", "stage", "examples", "note"],
        [
            [p["id"], p["affix"], p["type"], p["function"], str(p["stage"]),
             " | ".join("%s = %s (%s-)" % (x["ru"], x["gloss"], x["root"])
                        for x in p["examples"]),
             _s(p.get("note"))]
            for p in dataio.root_patterns()
        ],
    )
    _write_csv(
        os.path.join(CSV_DIR, "roots_items.csv"),
        ["id", "stage", "prompt", "prompt_ru", "options_lang", "options", "answer",
         "answer_text", "explain"],
        [
            [i["id"], str(i["stage"]), i["prompt"], _s(i.get("prompt_ru")),
             i["options_lang"], " | ".join(i["options"]), str(i["answer"]),
             i["options"][i["answer"]], _s(i.get("explain"))]
            for i in dataio.root_items()
        ],
    )


def export_reading_csv() -> None:
    _write_csv(
        os.path.join(CSV_DIR, "reading_passages.csv"),
        ["id", "stage", "level", "ru_level1", "ru_level3", "lafal", "gloss", "keep"],
        [
            [p["id"], str(p["stage"]), str(p["level"]), p["ru"],
             strip_stress(p["ru"]), pronounce_text(p["ru"]), p["gloss"],
             _s(p.get("keep"))]
            for p in dataio.reading_passages()
        ],
    )
    rows = []
    for i in dataio.reading_items():
        t = i.get("target")
        tw = target_word(i["full_ru"], t) if t is not None else ""
        rows.append([
            i["id"], i["type"], str(i["stage"]), str(i["level"]),
            render_item(i["full_ru"], i["level"], t), i["full_ru"],
            pronounce_text(i["full_ru"]), i["gloss"], _s(t),
            strip_stress(tw) if tw else "",
            " | ".join(i["options"]), str(i["answer"]), i["options"][i["answer"]],
            _s(i.get("option_glosses")), _s(i.get("explain")),
        ])
    _write_csv(
        os.path.join(CSV_DIR, "reading_items.csv"),
        ["id", "type", "stage", "level", "shown", "full_ru", "lafal", "gloss",
         "target_index", "target_word_bare", "options", "answer", "answer_text",
         "option_glosses", "explain"],
        rows,
    )


def export_falsefriends_csv() -> None:
    _write_csv(
        os.path.join(CSV_DIR, "falsefriends_entries.csv"),
        ["id", "ru", "translit", "lafal", "gloss", "mistaken", "correct", "kind",
         "stage", "note"],
        [
            [e["id"], e["ru"], translit(e["ru"]), pronounce_text(e["ru"]),
             e["gloss"], e["mistaken"], _s(e.get("correct")), e["kind"],
             str(e["stage"]), e["note"]]
            for e in dataio.falsefriend_entries()
        ],
    )
    _write_csv(
        os.path.join(CSV_DIR, "falsefriends_items.csv"),
        ["id", "stage", "prompt", "prompt_ru", "options_lang", "options", "answer",
         "answer_text", "explain"],
        [
            [i["id"], str(i["stage"]), i["prompt"], _s(i.get("prompt_ru")),
             i["options_lang"], " | ".join(i["options"]), str(i["answer"]),
             i["options"][i["answer"]], _s(i.get("explain"))]
            for i in dataio.falsefriend_items()
        ],
    )


# -------------------------------------------------------------------- anki ---

def export_anki_alphabet() -> None:
    rows = [
        [
            "%s %s" % (e["upper"], e["lower"]),
            "%s — %s" % (e["translit"], e["sound"]),
            e["name"],
            e["example"]["ru"],
            pronounce_text(e["example"]["ru"]),
            e["example"]["gloss"],
            e["note"],
            "rusia::alfabet rusia::%s rusia::tahap%d" % (e["group"], e["stage"]),
        ]
        for e in dataio.letters()
    ]
    _write_anki(os.path.join(ANKI_DIR, "alfabet.csv"), rows, tags_column=8)


def export_anki_vocab() -> None:
    rows = []
    for e in dataio.vocab_entries():
        rows.append([
            e["ru"],
            e["gloss"],
            vocab_detail(e),
            pronounce_text(e["ru"]),
            e["example"]["ru"],
            e["example"]["gloss"],
            translit(e["ru"]),
            _s(e.get("note")),
            "rusia::kosakata rusia::%s rusia::tahap%d" % (e["cat"], e["stage"]),
        ])
    _write_anki(os.path.join(ANKI_DIR, "kosakata.csv"), rows, tags_column=9)


def export_anki_grammar() -> None:
    rows = []
    for i in dataio.grammar_items():
        front = i["prompt"]
        if i.get("prompt_ru"):
            front += " / " + i["prompt_ru"]
        rows.append([
            front,
            i["options"][i["answer"]],
            _s(i.get("explain")),
            i["topic_title"],
            "rusia::tatabahasa rusia::%s rusia::tahap%d" % (i["topic_id"], i["stage"]),
        ])
    _write_anki(os.path.join(ANKI_DIR, "tatabahasa.csv"), rows, tags_column=5)


def export_anki_roots() -> None:
    rows = []
    for fam in dataio.root_families():
        for m in fam["members"]:
            rows.append([
                m["ru"],
                m["gloss"],
                fam["root"] + "-",
                fam["meaning"],
                m["pattern"],
                pronounce_text(m["ru"]),
                "rusia::akar rusia::%s rusia::tahap%d" % (fam["id"], fam["stage"]),
            ])
    _write_anki(os.path.join(ANKI_DIR, "akar.csv"), rows, tags_column=7)


def export_anki_reading() -> None:
    rows = []
    for p in dataio.reading_passages():
        rows.append([
            strip_stress(p["ru"]), p["ru"], pronounce_text(p["ru"]), p["gloss"],
            "Level %d" % p["level"],
            "rusia::baca rusia::level%d rusia::tahap%d" % (p["level"], p["stage"]),
        ])
    for i in dataio.reading_items():
        rows.append([
            render_item(i["full_ru"], i["level"], i.get("target")),
            i["full_ru"], pronounce_text(i["full_ru"]), i["gloss"],
            _s(i.get("explain")),
            "rusia::baca rusia::level%d rusia::tahap%d" % (i["level"], i["stage"]),
        ])
    _write_anki(os.path.join(ANKI_DIR, "baca.csv"), rows, tags_column=6)


def export_anki_falsefriends() -> None:
    rows = [
        [
            e["ru"],
            e["gloss"],
            "Sering disangka: " + e["mistaken"],
            _s(e.get("correct")),
            e["note"],
            "rusia::teman-palsu",
        ]
        for e in dataio.falsefriend_entries()
    ]
    _write_anki(os.path.join(ANKI_DIR, "teman-palsu.csv"), rows, tags_column=6)


def main() -> int:
    print("Membuat ekspor CSV dari data/*.json")
    print("data/csv/:")
    export_alphabet_csv()
    export_vocab_csv()
    export_grammar_csv()
    export_roots_csv()
    export_reading_csv()
    export_falsefriends_csv()
    print("anki/:")
    export_anki_alphabet()
    export_anki_vocab()
    export_anki_grammar()
    export_anki_roots()
    export_anki_reading()
    export_anki_falsefriends()
    print("Selesai.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Pemuat data dan pemeriksa skema.

Satu-satunya sumber data adalah berkas JSON di folder data/. Berkas CSV di
data/csv/, berkas di anki/, lembar kerja di worksheets/, dan webdata.js adalah
hasil ekspor yang dibuat ulang oleh skrip di tools/, bukan sumber yang
disunting langsung.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, "data")

MODULE_FILES = {
    "alphabet": "alphabet.json",
    "vocab": "vocab.json",
    "grammar": "grammar.json",
    "roots": "roots.json",
    "reading": "reading.json",
    "falsefriends": "falsefriends.json",
}

#: Kelas kata yang sah pada data/vocab.json.
POS_VALUES = {
    "ganti", "tunjuk", "tanya", "angka", "benda", "kerja", "sifat",
    "adverbia", "preposisi", "konjungsi", "partikel", "salam",
}

#: Gender yang sah. None hanya diizinkan untuk kata bukan benda, atau kata
#: benda yang hanya berbentuk jamak (pluralonly).
GENDER_VALUES = {"m", "f", "n", None}

ASPECT_VALUES = {"imperfektif", "perfektif", None}

#: Kategori tematik pada vocab.json beserta labelnya untuk tampilan.
CAT_LABEL = {
    "ganti": "Kata ganti",
    "tunjuk": "Kata tunjuk",
    "salam": "Salam & sopan",
    "tanya": "Kata tanya",
    "angka": "Angka",
    "keluarga": "Keluarga",
    "orang": "Orang",
    "benda": "Benda",
    "makanan": "Makanan",
    "tempat": "Tempat",
    "waktu": "Waktu",
    "kerja": "Kata kerja",
    "sifat": "Kata sifat",
    "kecil": "Kata tugas",
}

POS_LABEL = {
    "ganti": "kata ganti",
    "tunjuk": "kata tunjuk",
    "tanya": "kata tanya",
    "angka": "angka",
    "benda": "kata benda",
    "kerja": "kata kerja",
    "sifat": "kata sifat",
    "adverbia": "adverbia",
    "preposisi": "preposisi",
    "konjungsi": "konjungsi",
    "partikel": "partikel",
    "salam": "salam",
}

GENDER_LABEL = {"m": "maskulin", "f": "feminin", "n": "netral"}

GROUP_LABEL = {
    "sama": "Mirip Latin, bunyi sama",
    "palsu": "Mirip Latin, bunyi berbeda",
    "baru": "Bentuk baru",
    "tanda": "Tanda, bukan bunyi",
}

MAX_STAGE = 6


def _read_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=None)
def load(name: str) -> dict:
    """Muat satu modul data berdasarkan nama ('vocab', 'grammar', ...)."""
    if name not in MODULE_FILES:
        raise KeyError("modul tidak dikenal: %s" % name)
    return _read_json(os.path.join(DATA_DIR, MODULE_FILES[name]))


def load_all() -> dict[str, dict]:
    return {name: load(name) for name in MODULE_FILES}


def _upto(items: list[dict], stage: int | None) -> list[dict]:
    if stage is None:
        return list(items)
    return [i for i in items if i["stage"] <= stage]


# ----------------------------------------------------------------- alfabet ---

def letters(stage: int | None = None) -> list[dict]:
    return _upto(load("alphabet")["entries"], stage)


def letter_items(stage: int | None = None) -> list[dict]:
    return _upto(load("alphabet")["items"], stage)


# ---------------------------------------------------------------- kosakata ---

def vocab_entries(stage: int | None = None) -> list[dict]:
    return _upto(load("vocab")["entries"], stage)


# -------------------------------------------------------------- tatabahasa ---

def grammar_topics(stage: int | None = None) -> list[dict]:
    return _upto(load("grammar")["topics"], stage)


def grammar_items(stage: int | None = None) -> list[dict]:
    out: list[dict] = []
    for topic in grammar_topics(stage):
        for item in topic["items"]:
            out.append({
                **item,
                "topic_id": topic["id"],
                "topic_title": topic["title"],
                "stage": topic["stage"],
            })
    return out


# -------------------------------------------------------------------- akar ---

def root_families(stage: int | None = None) -> list[dict]:
    return _upto(load("roots")["families"], stage)


def root_patterns(stage: int | None = None) -> list[dict]:
    return _upto(load("roots")["patterns"], stage)


def root_items(stage: int | None = None) -> list[dict]:
    return _upto(load("roots")["items"], stage)


def root_of(word: str) -> list[dict]:
    """Keluarga akar yang memuat kata ini (dipakai pengujian silang)."""
    out = []
    for fam in root_families():
        if any(m["ru"] == word for m in fam["members"]):
            out.append(fam)
    return out


# -------------------------------------------------------------------- baca ---

def reading_passages(stage: int | None = None, level: int | None = None) -> list[dict]:
    out = _upto(load("reading")["passages"], stage)
    if level is not None:
        out = [p for p in out if p["level"] == level]
    return out


def reading_items(stage: int | None = None, level: int | None = None) -> list[dict]:
    out = _upto(load("reading")["items"], stage)
    if level is not None:
        out = [i for i in out if i["level"] == level]
    return out


# ------------------------------------------------------------ teman palsu ---

def falsefriend_entries(stage: int | None = None) -> list[dict]:
    return _upto(load("falsefriends")["entries"], stage)


def falsefriend_items(stage: int | None = None) -> list[dict]:
    return _upto(load("falsefriends")["items"], stage)


def usage_notes() -> list[dict]:
    return list(load("falsefriends")["usage_notes"])


# ------------------------------------------------------------------- kartu ---

def all_card_ids() -> list[str]:
    """Semua id yang dipakai sebagai kartu Leitner, dari seluruh modul."""
    ids: list[str] = []
    ids += [e["id"] for e in letters()]
    ids += [i["id"] for i in letter_items()]
    ids += [e["id"] for e in vocab_entries()]
    ids += [i["id"] for i in grammar_items()]
    ids += [f["id"] for f in root_families()]
    ids += [i["id"] for i in root_items()]
    ids += [p["id"] for p in reading_passages()]
    ids += [i["id"] for i in reading_items()]
    ids += [i["id"] for i in falsefriend_items()]
    return ids


__all__ = [
    "ASPECT_VALUES",
    "CAT_LABEL",
    "DATA_DIR",
    "GENDER_LABEL",
    "GENDER_VALUES",
    "GROUP_LABEL",
    "MAX_STAGE",
    "MODULE_FILES",
    "POS_LABEL",
    "POS_VALUES",
    "ROOT",
    "all_card_ids",
    "falsefriend_entries",
    "falsefriend_items",
    "grammar_items",
    "grammar_topics",
    "letter_items",
    "letters",
    "load",
    "load_all",
    "reading_items",
    "reading_passages",
    "root_families",
    "root_items",
    "root_of",
    "root_patterns",
    "usage_notes",
    "vocab_entries",
]

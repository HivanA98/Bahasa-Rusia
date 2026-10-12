"""Pengujian skema data: id unik, format id, tidak ada field kosong, nilai sah."""

from __future__ import annotations

import re

import pytest

from rusdrill import dataio

ID_PATTERNS = {
    "letter": re.compile(r"^a\d{2}$"),
    "letter_item": re.compile(r"^a-q\d{2}$"),
    "vocab": re.compile(r"^v\d{3}$"),
    "grammar_topic": re.compile(r"^g\d{2}$"),
    "grammar_item": re.compile(r"^g\d{2}-\d{2}$"),
    "root_family": re.compile(r"^r\d{2}$"),
    "root_pattern": re.compile(r"^w\d{2}$"),
    "root_item": re.compile(r"^r-q\d{2}$"),
    "reading_passage": re.compile(r"^rp\d{2}$"),
    "reading_item": re.compile(r"^rd-(q|m|p)\d{2}$"),
    "ff_entry": re.compile(r"^f\d{2}$"),
    "ff_item": re.compile(r"^f-q\d{2}$"),
}

#: Field yang boleh bernilai null atau tidak ada sama sekali. Field lain tidak
#: boleh null MAUPUN berupa teks kosong.
NULLABLE = {
    "gender", "plural", "aspect", "pair", "conj", "forms", "root", "root_note",
    "note", "prompt_ru", "target", "option_glosses", "variants", "explain",
    "caveats", "keep", "alt", "correct", "pluralonly", "stress_marked", "prompt",
}


def _check_no_empty(obj, where: str, problems: list[str]) -> None:
    """Rekursif: tolak string kosong dan nilai null pada field wajib."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if v is None and k not in NULLABLE:
                problems.append("%s.%s bernilai null" % (where, k))
            elif isinstance(v, str) and not v.strip() and k not in NULLABLE:
                problems.append("%s.%s berupa teks kosong" % (where, k))
            else:
                _check_no_empty(v, "%s.%s" % (where, k), problems)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str) and not v.strip():
                problems.append("%s[%d] berupa teks kosong" % (where, i))
            else:
                _check_no_empty(v, "%s[%d]" % (where, i), problems)


def test_semua_id_unik_di_seluruh_modul():
    ids = dataio.all_card_ids()
    ids += [t["id"] for t in dataio.grammar_topics()]
    ids += [p["id"] for p in dataio.root_patterns()]
    ids += [e["id"] for e in dataio.falsefriend_entries()]
    duplikat = sorted({i for i in ids if ids.count(i) > 1})
    assert not duplikat, "id ganda: %s" % duplikat


@pytest.mark.parametrize(
    "kind,items",
    [
        ("letter", dataio.letters()),
        ("letter_item", dataio.letter_items()),
        ("vocab", dataio.vocab_entries()),
        ("grammar_topic", dataio.grammar_topics()),
        ("grammar_item", dataio.grammar_items()),
        ("root_family", dataio.root_families()),
        ("root_pattern", dataio.root_patterns()),
        ("root_item", dataio.root_items()),
        ("reading_passage", dataio.reading_passages()),
        ("reading_item", dataio.reading_items()),
        ("ff_entry", dataio.falsefriend_entries()),
        ("ff_item", dataio.falsefriend_items()),
    ],
)
def test_format_id(kind, items):
    pola = ID_PATTERNS[kind]
    salah = [i["id"] for i in items if not pola.match(i["id"])]
    assert not salah, "format id tidak sesuai untuk %s: %s" % (kind, salah)


def test_tidak_ada_field_kosong():
    problems: list[str] = []
    for name in dataio.MODULE_FILES:
        _check_no_empty(dataio.load(name), name, problems)
    assert not problems, "\n".join(problems)


def test_nilai_pos_dan_gender_sah():
    salah = []
    for e in dataio.vocab_entries():
        if e["pos"] not in dataio.POS_VALUES:
            salah.append("%s: pos %r" % (e["id"], e["pos"]))
        if e.get("gender") not in dataio.GENDER_VALUES:
            salah.append("%s: gender %r" % (e["id"], e.get("gender")))
        if e.get("aspect") not in dataio.ASPECT_VALUES:
            salah.append("%s: aspect %r" % (e["id"], e.get("aspect")))
    assert not salah, salah


def test_kata_benda_bergender():
    """Setiap kata benda wajib bergender, kecuali yang hanya berbentuk jamak."""
    salah = [
        e["id"] for e in dataio.vocab_entries()
        if e["pos"] == "benda" and not e.get("gender") and not e.get("pluralonly")
    ]
    assert not salah, "kata benda tanpa gender: %s" % salah


def test_kata_kerja_punya_aspek_dan_konjugasi():
    tanpa_aspek = [
        e["id"] for e in dataio.vocab_entries()
        if e["pos"] == "kerja" and not e.get("aspect")
    ]
    assert not tanpa_aspek, "kata kerja tanpa aspek: %s" % tanpa_aspek
    # быть sengaja tidak memiliki konjugasi kala kini; itulah ciri khasnya.
    tanpa_conj = [
        e["id"] for e in dataio.vocab_entries()
        if e["pos"] == "kerja" and not e.get("conj") and e["ru"] != "быть"
    ]
    assert not tanpa_conj, "kata kerja tanpa konjugasi: %s" % tanpa_conj
    for e in dataio.vocab_entries():
        if e.get("conj"):
            assert set(e["conj"]) == {"sg1", "sg2", "sg3"}, e["id"]


def test_kata_sifat_punya_bentuk_gender():
    kurang = [
        e["id"] for e in dataio.vocab_entries()
        if e["pos"] == "sifat" and set(e.get("forms") or {}) != {"f", "n", "pl"}
    ]
    assert not kurang, "kata sifat tanpa bentuk f/n/pl lengkap: %s" % kurang


def test_setiap_tahap_terisi():
    for stage in range(1, dataio.MAX_STAGE + 1):
        assert [e for e in dataio.vocab_entries() if e["stage"] == stage], \
            "tahap kosakata %d kosong" % stage
    tahap_grammar = {t["stage"] for t in dataio.grammar_topics()}
    assert tahap_grammar <= set(range(1, dataio.MAX_STAGE + 1))
    assert len(tahap_grammar) >= 4


def test_setiap_level_baca_terisi():
    for level in (1, 2, 3):
        assert dataio.reading_passages(level=level), "level %d tanpa teks" % level
        assert dataio.reading_items(level=level), "level %d tanpa soal" % level


def test_alfabet_lengkap_33_huruf():
    huruf = dataio.letters()
    assert len(huruf) == 33, "alfabet Rusia berisi 33 huruf, ditemukan %d" % len(huruf)
    kecil = [e["lower"] for e in huruf]
    assert len(set(kecil)) == 33, "ada huruf yang ditulis dua kali"
    vokal = [e for e in huruf if e["type"] == "vokal"]
    assert len(vokal) == 10, "bahasa Rusia memiliki 10 huruf vokal, ditemukan %d" % len(vokal)
    tanda = [e for e in huruf if e["type"] == "tanda"]
    assert len(tanda) == 2, "hanya ada dua tanda: ь dan ъ"
    assert {e["lower"] for e in tanda} == {"ь", "ъ"}


def test_setiap_kelompok_huruf_terisi():
    grup = {e["group"] for e in dataio.letters()}
    assert grup == {"sama", "palsu", "baru", "tanda"}


def test_keep_pada_teks_baca_masih_di_dalam_jangkauan():
    salah = []
    for p in dataio.reading_passages():
        n = len(p["ru"].split(" "))
        for k in p.get("keep") or []:
            if not (0 <= k < n):
                salah.append("%s: keep %d dari %d kata" % (p["id"], k, n))
    assert not salah, salah


def test_pasangan_aspek_saling_menunjuk_bila_keduanya_ada():
    by_ru = {e["ru"]: e for e in dataio.vocab_entries()}
    salah = []
    for e in dataio.vocab_entries():
        pair = e.get("pair")
        if pair and pair in by_ru:
            lawan = by_ru[pair]
            if lawan.get("pair") != e["ru"]:
                salah.append("%s dan %s tidak saling menunjuk" % (e["ru"], pair))
            if lawan.get("aspect") == e.get("aspect"):
                salah.append("%s dan %s beraspek sama" % (e["ru"], pair))
    assert not salah, salah

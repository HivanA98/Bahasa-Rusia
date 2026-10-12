"""Pengujian ortografi: hanya huruf Kiril, bentuk NFC, dan tanda tekanan.

Yang diperiksa di sini adalah BENTUK PENULISAN, bukan kebenaran isi bahasa.
Letak tekanan yang keliru pada sebuah kata tidak bisa dideteksi mesin; yang
bisa dipastikan hanyalah bahwa setiap kata bersuku banyak memiliki tepat satu
tanda tekanan. Lihat data/NEEDS_REVIEW.md.
"""

from __future__ import annotations

import re
import unicodedata

import pytest

from rusdrill import dataio
from rusdrill.cyrillic import (
    check_chars,
    check_stress,
    check_stress_word,
    count_vowels,
    has_cyrillic,
    is_nfc,
    pronounce,
    strip_stress,
    strip_stress_and_yo,
    stress_position,
    syllables,
    validate,
)

STRESS = "́"


# --------------------------------------------------------- unit: tekanan ---

def test_kata_bersuku_banyak_wajib_bertanda():
    assert check_stress_word("работа")  # работа tanpa tanda
    assert not check_stress_word("рабо" + STRESS + "та")


def test_kata_bersuku_satu_tanpa_tanda():
    assert not check_stress_word("нет")               # нет
    assert check_stress_word("не" + STRESS + "т")     # не́т


def test_kata_ber_yo_tidak_diberi_tanda():
    assert not check_stress_word("ещё")               # ещё
    assert check_stress_word("ещё" + STRESS)


def test_dua_tanda_ditolak():
    ganda = "мо" + STRESS + "локо" + STRESS
    assert check_stress_word(ganda)


def test_tanda_wajib_mengikuti_vokal():
    salah = "работ" + STRESS + "а"     # tanda sesudah т
    assert any("vokal" in p for p in check_chars(salah))


def test_huruf_latin_ditolak():
    assert check_chars("рабоaта")      # ada 'a' Latin


def test_strip_stress_mempertahankan_yo():
    assert strip_stress("ещё") == "ещё"
    assert strip_stress("рабо" + STRESS + "та") == \
        "работа"


def test_strip_stress_and_yo_mengganti_yo():
    assert strip_stress_and_yo("ещё") == "еще"


def test_jumlah_vokal_sama_dengan_jumlah_suku():
    assert count_vowels("молоко") == 3
    assert len(syllables("молоко")) == 3


def test_posisi_tekanan():
    assert stress_position("молоко" + STRESS) == 2
    assert stress_position("ещё") == 1          # ё selalu bertekanan
    assert stress_position("нет") == 0          # bersuku satu
    assert stress_position("работа") is None


def test_has_cyrillic():
    assert has_cyrillic("дом")
    assert not has_cyrillic("rumah (kata benda)")


# ------------------------------------------------------- unit: pelafalan ---

#: Kasus yang dipatok. Bila kaidah di cyrillic.py diubah, pengujian ini akan
#: memberi tahu apa saja yang ikut berubah.
LAFAL = [
    ("молоко" + STRESS, "ma-la-KO"),
    ("рабо" + STRESS + "та", "ra-BO-ta"),
    ("что", "shto"),
    ("его" + STRESS, "yi-VO"),
    ("сего" + STRESS + "дня", "si-VO-dnya"),
    ("хлеб", "khlyep"),
    ("го" + STRESS + "род", "GO-rat"),
    ("учи" + STRESS + "ться", "u-CHI-tsa"),
    ("по" + STRESS + "здно", "PO-zna"),
    ("то" + STRESS + "лько", "TOL'-ka"),
    ("мать", "mat'"),
    ("ещё", "i-SHCHO"),
]


@pytest.mark.parametrize("kata,lafal", LAFAL)
def test_pelafalan_dipatok(kata, lafal):
    assert pronounce(kata) == lafal


def test_vokal_o_tanpa_tekanan_menjadi_a():
    assert "ma" in pronounce("молоко" + STRESS)


def test_suku_bertekanan_ditulis_huruf_besar():
    hasil = pronounce("рабо" + STRESS + "та")
    assert "BO" in hasil and hasil.count("-") == 2


# ------------------------------------------------------------ data: ejaan ---

def _ru_fields():
    """Semua teks Kiril di dalam data, beserta tempatnya."""
    out: list[tuple[str, str]] = []
    for e in dataio.letters():
        out.append(("%s.upper" % e["id"], e["upper"]))
        out.append(("%s.lower" % e["id"], e["lower"]))
        out.append(("%s.name" % e["id"], e["name"]))
        out.append(("%s.example" % e["id"], e["example"]["ru"]))
    for i in dataio.letter_items():
        if i.get("prompt_ru") and i.get("stress_marked", True):
            out.append(("%s.prompt_ru" % i["id"], i["prompt_ru"]))
        if i["options_lang"] == "ru":
            for o in i["options"]:
                out.append(("%s.option" % i["id"], o))
    for e in dataio.vocab_entries():
        out.append(("%s.ru" % e["id"], e["ru"]))
        for f in ("plural", "pair"):
            if e.get(f):
                out.append(("%s.%s" % (e["id"], f), e[f]))
        for k, v in (e.get("conj") or {}).items():
            out.append(("%s.conj.%s" % (e["id"], k), v))
        for k, v in (e.get("forms") or {}).items():
            out.append(("%s.forms.%s" % (e["id"], k), v))
        out.append(("%s.example" % e["id"], e["example"]["ru"]))
    for t in dataio.grammar_topics():
        for x in t["examples"]:
            out.append(("%s.example" % t["id"], x["ru"]))
    for i in dataio.grammar_items() + dataio.falsefriend_items() + dataio.root_items():
        if i.get("prompt_ru") and i.get("stress_marked", True):
            out.append(("%s.prompt_ru" % i["id"], i["prompt_ru"]))
        if i["options_lang"] == "ru":
            for o in i["options"]:
                out.append(("%s.option" % i["id"], o))
    for f in dataio.root_families():
        for m in f["members"]:
            out.append(("%s.member" % f["id"], m["ru"]))
    for p in dataio.root_patterns():
        for x in p["examples"]:
            out.append(("%s.example" % p["id"], x["ru"]))
    for p in dataio.reading_passages():
        out.append(("%s.ru" % p["id"], p["ru"]))
    for i in dataio.reading_items():
        out.append(("%s.full_ru" % i["id"], i["full_ru"]))
        if i["options_lang"] == "ru":
            for o in i["options"]:
                out.append(("%s.option" % i["id"], o))
    for e in dataio.falsefriend_entries():
        out.append(("%s.ru" % e["id"], e["ru"]))
        if e.get("correct"):
            out.append(("%s.correct" % e["id"], e["correct"]))
    return out


def test_semua_teks_kiril_sah():
    problems = []
    for where, text in _ru_fields():
        problems += ["%s: %s" % (where, p) for p in validate(text)]
    assert not problems, "\n".join(problems)


def test_semua_teks_dalam_bentuk_nfc():
    salah = [where for where, text in _ru_fields() if not is_nfc(text)]
    assert not salah, salah


def test_akar_kata_tanpa_tanda_tekanan():
    """Akar adalah potongan kata, bukan kata, sehingga tidak diberi tanda."""
    problems = []
    for f in dataio.root_families():
        for root in [f["root"]] + (f.get("variants") or []):
            problems += ["%s: %s" % (f["id"], p)
                         for p in check_chars(root, allow_punct=False)]
            if STRESS in root:
                problems.append("%s: akar %s bertanda tekanan" % (f["id"], root))
    for e in dataio.vocab_entries():
        if e.get("root") and STRESS in e["root"]:
            problems.append("%s: akar bertanda tekanan" % e["id"])
    assert not problems, problems


def test_contoh_kalimat_diakhiri_tanda_baca():
    kurang = [
        e["id"] for e in dataio.vocab_entries()
        if e["example"]["ru"].strip()[-1] not in ".!?"
    ]
    assert not kurang, "contoh kalimat tanpa tanda akhir: %s" % kurang


# ------------------------------------------------- data: seluruh teks ---
# Tiga pengujian berikut menyapu SEMUA teks di dalam data/, termasuk field
# prosa (note, explain, explanation, caveats) yang tidak dijangkau validator
# tanda tekanan. Ketiganya menangkap kesalahan yang mudah lolos dari mata
# manusia karena bentuk hurufnya nyaris sama.

#: Tanda hubung dan tanda baca menjadi pemisah kata, karena prosa Indonesia
#: memang menyambung awalan Latin dengan kata Kiril: "kata ber-на".
_KATA = re.compile(r"[\ẃ']+", re.UNICODE)
_KIRIL = re.compile(r"[Ѐ-ӿ]")
_LATIN = re.compile(r"[A-Za-z]")


def _semua_teks():
    """Setiap teks di seluruh berkas data, beserta tempatnya."""

    def jelajah(obj, where):
        if isinstance(obj, dict):
            for k, v in obj.items():
                yield from jelajah(v, "%s.%s" % (where, k))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                yield from jelajah(v, "%s[%d]" % (where, i))
        elif isinstance(obj, str):
            yield where, obj

    for name in dataio.MODULE_FILES:
        yield from jelajah(dataio.load(name), name)


def test_tidak_ada_kata_bercampur_aksara_latin_dan_kiril():
    """Satu kata tidak boleh memuat huruf Latin dan Kiril sekaligus.

    Huruf seperti а, е, о, р, с, у, х, М, Н, Т hampir tidak terbedakan dari
    pasangan Latinnya di layar, sehingga salah taip semacam `menjadи` atau
    `Idти́` bisa bertahan lama tanpa terlihat. Mesin membedakannya dengan
    pasti, dan itulah gunanya pengujian ini.
    """
    salah = []
    for where, teks in _semua_teks():
        for kata in _KATA.findall(teks):
            if _KIRIL.search(kata) and _LATIN.search(kata):
                salah.append("%s: %r" % (where, kata))
    assert not salah, (
        "kata bercampur aksara Latin dan Kiril:\n  " + "\n  ".join(salah)
    )


def test_tidak_ada_huruf_latin_beraksen_di_data():
    """Alih huruf Latin tidak boleh masuk ke data.

    Data hanya memuat Bahasa Indonesia dan tulisan Kiril. Huruf Latin
    beraksen (á, ó, é) adalah tanda bahwa alih huruf seperti `Krásnaya
    plóshchad` menyelinap masuk, padahal tempatnya di keluaran program, bukan
    di sumber datanya.
    """
    salah = []
    for where, teks in _semua_teks():
        for ch in teks:
            if ord(ch) > 127 and unicodedata.name(ch, "").startswith("LATIN"):
                salah.append("%s: %r pada %r" % (where, ch, teks[:60]))
    assert not salah, (
        "huruf Latin beraksen di dalam data:\n  " + "\n  ".join(salah)
    )


def test_seluruh_teks_data_dalam_bentuk_nfc():
    """Termasuk field prosa, bukan hanya field Kiril.

    Teks NFD terlihat sama persis di layar tetapi berbeda isinya, sehingga
    pencarian dan penyuntingan pada teks itu bisa gagal tanpa alasan yang
    kelihatan.
    """
    salah = [
        "%s: %r" % (where, teks[:60])
        for where, teks in _semua_teks()
        if not unicodedata.is_normalized("NFC", teks)
    ]
    assert not salah, "teks tidak dalam bentuk NFC:\n  " + "\n  ".join(salah)

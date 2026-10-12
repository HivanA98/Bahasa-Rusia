"""Pengujian kunci jawaban: tepat satu jawaban benar, pengecoh tidak ikut benar.

Pengujian terpenting di berkas ini adalah test_pilihan_stress_choice_berhuruf_sama:
semua pilihan pada soal "di mana letak tekanan" WAJIB tersusun dari huruf yang
sama persis, sehingga soal tidak bisa dijawab hanya dengan melihat bentuk
katanya.
"""

from __future__ import annotations

import random

import pytest

from rusdrill import dataio
from rusdrill.cyrillic import PUNCT, strip_stress
from rusdrill.questions import (
    accepted_set,
    build_pool,
    normalize,
    odd_one_out,
    root_of_word,
    target_word,
    vocab_id_to_ru,
)

ALL_ITEMS = (
    dataio.letter_items()
    + dataio.grammar_items()
    + dataio.root_items()
    + dataio.reading_items()
    + dataio.falsefriend_items()
)


def test_setiap_soal_punya_kunci_yang_sah():
    salah = [
        i["id"] for i in ALL_ITEMS
        if not (0 <= i["answer"] < len(i["options"]))
    ]
    assert not salah, salah


def test_tidak_ada_pilihan_identik():
    salah = [i["id"] for i in ALL_ITEMS if len(set(i["options"])) != len(i["options"])]
    assert not salah, salah


def test_setiap_soal_punya_minimal_dua_pilihan():
    salah = [i["id"] for i in ALL_ITEMS if len(i["options"]) < 2]
    assert not salah, salah


def test_options_lang_sah():
    salah = [i["id"] for i in ALL_ITEMS if i["options_lang"] not in ("ru", "id")]
    assert not salah, salah


def test_pilihan_stress_choice_berhuruf_sama():
    """Semua pilihan harus berhuruf sama; yang berbeda hanya letak tekanan."""
    salah = []
    for i in dataio.reading_items():
        if i["type"] != "stress_choice":
            continue
        bare = {strip_stress(o).lower() for o in i["options"]}
        if len(bare) != 1:
            salah.append("%s: huruf pilihan berbeda-beda: %s" % (i["id"], bare))
    assert not salah, salah


def test_kunci_stress_choice_sama_dengan_kata_di_kalimat():
    salah = []
    for i in dataio.reading_items():
        if i["type"] != "stress_choice":
            continue
        kata = target_word(i["full_ru"], i["target"])
        kunci = i["options"][i["answer"]]
        if kunci != kata:
            salah.append("%s: kunci %r, kalimat %r" % (i["id"], kunci, kata))
    assert not salah, salah


def test_target_stress_choice_di_dalam_jangkauan():
    salah = []
    for i in dataio.reading_items():
        if i["type"] != "stress_choice":
            continue
        n = len(i["full_ru"].split(" "))
        if not (0 <= i["target"] < n):
            salah.append(i["id"])
    assert not salah, salah


def test_option_glosses_sejumlah_pilihan():
    salah = []
    for i in dataio.reading_items():
        g = i.get("option_glosses")
        if g and len(g) != len(i["options"]):
            salah.append(i["id"])
    assert not salah, salah


def test_pengecoh_kosakata_tidak_ikut_benar():
    """Pengecoh soal Indonesia ke Rusia tidak boleh menerima arti yang ditanyakan.

    Tanpa saringan ini, pertanyaan "kata Rusia untuk 'malam'" bisa memuat ночь
    dan ве́чер sekaligus, sehingga ada dua jawaban yang sama-sama benar.
    """
    rng = random.Random(0)
    pool = dataio.vocab_entries()
    by_ru = {e["ru"]: e for e in pool}
    salah = []
    for e in pool:
        q = vocab_id_to_ru(e, pool, rng)
        kunci = normalize(e["gloss"])
        for i, o in enumerate(q.options):
            if i == q.answer:
                continue
            lawan = by_ru.get(o)
            if lawan and kunci in accepted_set(lawan):
                salah.append("%s: pengecoh %s juga berarti %r" % (e["id"], o, e["gloss"]))
    assert not salah, salah


def test_soal_akar_buatan_otomatis_tidak_punya_dua_jawaban():
    """Pada soal 'mana yang BUKAN sekeluarga', pengecoh harus benar-benar asing."""
    rng = random.Random(1)
    fams = dataio.root_families()
    for _ in range(20):
        for fam in fams:
            q = odd_one_out(fam, fams, rng)
            anggota = {m["ru"] for m in fam["members"]}
            asing = [o for o in q.options if o not in anggota]
            assert len(asing) == 1, "%s: %s" % (fam["id"], q.options)
            assert q.options[q.answer] == asing[0]


def test_soal_akar_apa_akarnya_kuncinya_dari_data():
    rng = random.Random(2)
    fams = dataio.root_families()
    for fam in fams:
        q = root_of_word(fam, fams, rng)
        assert q.options[q.answer] == fam["root"]
        assert len(set(q.options)) == len(q.options)


@pytest.mark.parametrize("mode", ["alfabet", "kosakata-id", "tatabahasa", "akar", "baca"])
def test_semua_soal_pilihan_ganda_punya_kunci(mode):
    rng = random.Random(3)
    for q in build_pool(mode, None, rng):
        if q.kind != "mcq":
            continue
        assert q.options and q.answer is not None
        assert 0 <= q.answer < len(q.options)
        assert len(set(q.options)) == len(q.options), q.card_id


def test_jawaban_bertaip_menerima_arti_utama():
    rng = random.Random(4)
    for q in build_pool("kosakata-ru", None, rng):
        assert q.accepted, q.card_id
        assert q.is_correct_text(q.accepted[0])


def test_kata_yang_ditanyakan_tidak_terlihat_pada_soal():
    """Tanda tekanan kata sasaran harus hilang dari kalimat yang ditampilkan."""
    rng = random.Random(5)
    for q in build_pool("baca", None, rng):
        if q.stimulus_label is None:
            continue
        sasaran = q.stimulus_label.split(": ", 1)[1]
        kata_tampil = [
            "".join(c for c in w if c not in PUNCT) for w in q.stimulus_ru.split(" ")
        ]
        assert sasaran in kata_tampil, q.card_id
        assert "́" not in sasaran, "%s: jawabannya terlihat" % q.card_id

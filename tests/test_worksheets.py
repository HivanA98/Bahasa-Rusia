"""Pengujian lembar kerja: kunci terpisah, bagian lengkap, butir berasal dari data."""

from __future__ import annotations

import io
import os
import re

import pytest

from conftest import ROOT
from rusdrill import dataio
from rusdrill.cyrillic import strip_stress

WS_DIR = os.path.join(ROOT, "worksheets")
KEY_DIR = os.path.join(WS_DIR, "answers")
NOMOR = list(range(1, 13))

BAGIAN = [
    "## A. Tulis bunyi dan nama huruf",
    "## B. Tulis arti kata",
    "## C. Tulis kata Rusia",
    "## D. Tata bahasa",
    "## E. Akar kata",
    "## F. Tekanan dan pelafalan",
]


def _read(path: str) -> str:
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def _ws(n: int) -> str:
    return _read(os.path.join(WS_DIR, "ws-%02d.md" % n))


def _key(n: int) -> str:
    return _read(os.path.join(KEY_DIR, "ws-%02d-kunci.md" % n))


@pytest.mark.parametrize("n", NOMOR)
def test_lembar_dan_kunci_ada(n):
    assert os.path.exists(os.path.join(WS_DIR, "ws-%02d.md" % n))
    assert os.path.exists(os.path.join(KEY_DIR, "ws-%02d-kunci.md" % n))


@pytest.mark.parametrize("n", NOMOR)
def test_semua_bagian_ada(n):
    teks = _ws(n)
    for judul in BAGIAN:
        assert judul in teks, "lembar %02d tanpa bagian %r" % (n, judul)


@pytest.mark.parametrize("n", NOMOR)
def test_lembar_kerja_tidak_memuat_jawaban(n):
    """Jawaban pilihan ganda hanya boleh ada di berkas kunci."""
    teks = _ws(n)
    assert "**a**" not in teks and "**b**" not in teks
    assert "Jawaban: ____" in teks
    assert "Kunci jawaban: `worksheets/answers/" in teks


@pytest.mark.parametrize("n", NOMOR)
def test_kunci_menunjuk_balik_ke_soalnya(n):
    assert "worksheets/ws-%02d.md" % n in _key(n)


@pytest.mark.parametrize("n", NOMOR)
def test_soal_tekanan_disajikan_tanpa_tanda(n):
    """Bagian F harus tanpa tanda tekanan; kuncinya bertanda penuh."""
    teks = _ws(n)
    bagian = teks.split("## F. Tekanan dan pelafalan", 1)[1]
    soal = [b for b in bagian.splitlines() if re.match(r"^\d+\. ", b)]
    assert soal, "lembar %02d tanpa soal tekanan" % n
    for b in soal:
        assert "́" not in b, "lembar %02d: tanda tekanan bocor di soal" % n
    kunci = _key(n).split("## F. Tekanan dan pelafalan", 1)[1]
    assert "́" in kunci, "kunci %02d tanpa tanda tekanan" % n


@pytest.mark.parametrize("n", NOMOR)
def test_butir_berasal_dari_data(n):
    """Setiap kata pada bagian B benar-benar ada di data kosakata."""
    kata = {e["ru"] for e in dataio.vocab_entries()}
    teks = _ws(n)
    bagian = teks.split("## B. Tulis arti kata", 1)[1].split("## C.", 1)[0]
    baris = [b for b in bagian.splitlines() if b.startswith("| ") and "|" in b[2:]]
    isi = [b.split("|")[2].strip() for b in baris if b.split("|")[1].strip().isdigit()]
    assert isi, "lembar %02d tanpa butir kosakata" % n
    asing = [k for k in isi if k not in kata]
    assert not asing, "butir yang tidak ada di data: %s" % asing


@pytest.mark.parametrize("n", NOMOR)
def test_huruf_pada_bagian_a_berasal_dari_alfabet(n):
    huruf = {"%s %s" % (e["upper"], e["lower"]) for e in dataio.letters()}
    bagian = _ws(n).split("## A.", 1)[1].split("## B.", 1)[0]
    baris = [b for b in bagian.splitlines() if b.startswith("| ")]
    isi = [b.split("|")[2].strip() for b in baris if b.split("|")[1].strip().isdigit()]
    asing = [k for k in isi if k not in huruf]
    assert not asing, "huruf yang tidak ada di data: %s" % asing


def test_tahap_lembar_naik_berurutan():
    for n in NOMOR:
        tahap = (n + 1) // 2
        assert "tahap %d" % tahap in _ws(n).splitlines()[0]


def test_lembar_awal_hanya_memakai_materi_tahap_awal():
    """Lembar 01 dan 02 tidak boleh memuat kata dari tahap yang belum dibuka."""
    tahap1 = {e["ru"] for e in dataio.vocab_entries(stage=1)}
    for n in (1, 2):
        bagian = _ws(n).split("## B. Tulis arti kata", 1)[1].split("## C.", 1)[0]
        baris = [b for b in bagian.splitlines() if b.startswith("| ")]
        isi = [b.split("|")[2].strip() for b in baris
               if b.split("|")[1].strip().isdigit()]
        asing = [k for k in isi if k not in tahap1]
        assert not asing, "lembar %02d memuat materi di luar tahap 1: %s" % (n, asing)


def test_daftar_isi_lembar_kerja_lengkap():
    readme = _read(os.path.join(WS_DIR, "README.md"))
    for n in NOMOR:
        assert "ws-%02d.md" % n in readme
        assert "ws-%02d-kunci.md" % n in readme


def test_kata_kunci_pada_bagian_f_tanpa_tanda_tekanan():
    """Kata kunci yang disebut di soal tidak boleh membocorkan tekanannya."""
    for n in NOMOR:
        bagian = _ws(n).split("## F.", 1)[1]
        for m in re.finditer(r"\(kata kunci: ([^)]+)\)", bagian):
            kata = m.group(1)
            assert kata == strip_stress(kata)

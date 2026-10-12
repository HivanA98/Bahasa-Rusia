"""Pengujian hasil ekspor: semuanya harus mutakhir terhadap data/*.json.

Bila data sudah disunting tetapi skrip di tools/ belum dijalankan ulang,
pengujian di berkas ini gagal dan menyebutkan perintah yang perlu dijalankan.
"""

from __future__ import annotations

import io
import json
import os
import re

import pytest

from conftest import ROOT, load_tool
from rusdrill import dataio

PERINTAH = {
    "csv": "python tools/build_exports.py",
    "web": "python tools/build_web.py",
    "ws": "python tools/build_worksheets.py",
}


def _read(path: str) -> str:
    with io.open(path, encoding="utf-8", newline="") as f:
        return f.read()


# ------------------------------------------------------------------- csv ---

@pytest.fixture(scope="module")
def exports_segar(tmp_path_factory):
    """Jalankan ulang build_exports.py ke folder sementara."""
    tmp = tmp_path_factory.mktemp("exports")
    tool = load_tool("build_exports")
    tool.CSV_DIR = os.path.join(str(tmp), "csv")
    tool.ANKI_DIR = os.path.join(str(tmp), "anki")
    tool.main()
    return str(tmp)


@pytest.mark.parametrize("nama", [
    "alphabet.csv", "vocab.csv", "grammar_topics.csv", "grammar_items.csv",
    "roots_families.csv", "roots_patterns.csv", "roots_items.csv",
    "reading_passages.csv", "reading_items.csv",
    "falsefriends_entries.csv", "falsefriends_items.csv",
])
def test_csv_mutakhir(nama, exports_segar):
    lama = os.path.join(ROOT, "data", "csv", nama)
    baru = os.path.join(exports_segar, "csv", nama)
    assert os.path.exists(lama), "%s belum dibuat. Jalankan %s" % (nama, PERINTAH["csv"])
    assert _read(lama) == _read(baru), \
        "%s tidak mutakhir. Jalankan %s" % (nama, PERINTAH["csv"])


@pytest.mark.parametrize("nama", [
    "alfabet.csv", "kosakata.csv", "tatabahasa.csv", "akar.csv", "baca.csv",
    "teman-palsu.csv",
])
def test_anki_mutakhir(nama, exports_segar):
    lama = os.path.join(ROOT, "anki", nama)
    baru = os.path.join(exports_segar, "anki", nama)
    assert os.path.exists(lama), "%s belum dibuat. Jalankan %s" % (nama, PERINTAH["csv"])
    assert _read(lama) == _read(baru), \
        "%s tidak mutakhir. Jalankan %s" % (nama, PERINTAH["csv"])


def test_anki_memakai_pengarah_dan_kolom_tag():
    for nama in ("alfabet.csv", "kosakata.csv", "tatabahasa.csv", "akar.csv",
                 "baca.csv", "teman-palsu.csv"):
        teks = _read(os.path.join(ROOT, "anki", nama))
        baris = teks.splitlines()
        assert baris[0] == "#separator:Comma"
        assert baris[1] == "#html:false"
        assert baris[2].startswith("#tags column:")


def test_anki_jumlah_kartu_sesuai_data():
    def n_kartu(nama):
        return len([
            b for b in _read(os.path.join(ROOT, "anki", nama)).splitlines()
            if b and not b.startswith("#")
        ])
    # Kartu Anki ditulis dengan tanda kutip penuh sehingga satu kartu bisa
    # memuat baris baru; hitung lewat csv agar tepat.
    import csv as _csv
    def n_baris(nama):
        with io.open(os.path.join(ROOT, "anki", nama), encoding="utf-8", newline="") as f:
            isi = [r for r in f if not r.startswith("#")]
        return len(list(_csv.reader(isi)))
    assert n_baris("alfabet.csv") == len(dataio.letters())
    assert n_baris("kosakata.csv") == len(dataio.vocab_entries())
    assert n_baris("tatabahasa.csv") == len(dataio.grammar_items())
    assert n_baris("teman-palsu.csv") == len(dataio.falsefriend_entries())
    assert n_kartu("akar.csv") >= len(dataio.root_families())


# ------------------------------------------------------------- webdata.js ---

def test_webdata_mutakhir(tmp_path):
    tool = load_tool("build_web")
    asli = tool.OUT
    tool.OUT = str(tmp_path / "webdata.js")
    try:
        tool.main()
        baru = _read(tool.OUT)
    finally:
        tool.OUT = asli
    lama = _read(os.path.join(ROOT, "webdata.js"))
    assert lama == baru, "webdata.js tidak mutakhir. Jalankan %s" % PERINTAH["web"]


def _webdata() -> dict:
    teks = _read(os.path.join(ROOT, "webdata.js"))
    awal = teks.index("{")
    akhir = teks.rindex("}") + 1
    return json.loads(teks[awal:akhir])


def test_webdata_hanya_ascii():
    """Teks Kiril ditulis sebagai escape agar tidak bergantung charset peladen."""
    teks = _read(os.path.join(ROOT, "webdata.js"))
    bukan_ascii = [c for c in teks if ord(c) > 127]
    assert not bukan_ascii, "webdata.js memuat karakter non-ASCII"


def test_webdata_jumlahnya_sesuai_data():
    d = _webdata()
    assert len(d["kosakata"]) == len(dataio.vocab_entries())
    assert len(d["tatabahasa"]) == len(dataio.grammar_items()) + len(dataio.falsefriend_items())
    assert len(d["palsu"]) == len(dataio.falsefriend_entries())
    assert len(d["topik"]) == len(dataio.grammar_topics())
    assert len(d["afiks"]) == len(dataio.root_patterns())
    assert len(d["baca"]) == len(dataio.reading_passages()) + len(dataio.reading_items())
    assert len(d["alfabet"]) == len(dataio.letters()) + len(dataio.letter_items())


def test_kunci_soal_di_webdata_sama_dengan_data():
    d = _webdata()
    oleh_id = {x["id"]: x for x in d["tatabahasa"]}
    for i in dataio.grammar_items() + dataio.falsefriend_items():
        w = oleh_id[i["id"]]
        assert w["answer"] == i["answer"], i["id"]
        assert w["options"] == i["options"], i["id"]
    baca = {x["id"]: x for x in d["baca"] if x["kind"] == "soal"}
    for i in dataio.reading_items():
        assert baca[i["id"]]["answer"] == i["answer"], i["id"]


def test_webdata_tidak_membocorkan_tanda_tekanan_pada_soal():
    """Kata yang ditanyakan harus tampil tanpa tanda tekanan."""
    d = _webdata()
    for x in d["baca"]:
        if x.get("kind") == "soal" and x.get("targetBare"):
            assert "́" not in x["targetBare"], x["id"]
            assert x["targetBare"] in x["shown"], x["id"]


def _tanpa_komentar(js: str) -> str:
    """Buang komentar JavaScript, supaya kata di dalam komentar tidak ikut diperiksa."""
    js = re.sub(r"/\*.*?\*/", "", js, flags=re.S)
    return re.sub(r"(^|\s)//[^\n]*", " ", js)


def test_aplikasi_web_tidak_memakai_fetch():
    """Supaya index.html tetap bisa dibuka langsung lewat file://."""
    app = _tanpa_komentar(_read(os.path.join(ROOT, "app.js")))
    assert "fetch(" not in app
    assert "XMLHttpRequest" not in app
    html = _read(os.path.join(ROOT, "index.html"))
    assert "webdata.js" in html and "app.js" in html


def test_jumlah_tab_sama_dengan_modul_di_webdata():
    html = _read(os.path.join(ROOT, "index.html"))
    mode = set(re.findall(r'data-mode="([a-z]+)"', html))
    d = _webdata()
    assert mode == {"alfabet", "kosakata", "tatabahasa", "akar", "baca", "palsu"}
    for m in mode:
        assert m in d, m


# ------------------------------------------------------------ worksheets ---

def test_lembar_kerja_mutakhir(tmp_path):
    tool = load_tool("build_worksheets")
    tool.WS_DIR = str(tmp_path)
    tool.KEY_DIR = str(tmp_path / "answers")
    tool.main()
    for nomor, _ in tool.PLAN:
        nama = "ws-%02d.md" % nomor
        lama = os.path.join(ROOT, "worksheets", nama)
        baru = os.path.join(str(tmp_path), nama)
        assert _read(lama) == _read(baru), \
            "%s tidak mutakhir. Jalankan %s" % (nama, PERINTAH["ws"])
        kunci = "ws-%02d-kunci.md" % nomor
        assert _read(os.path.join(ROOT, "worksheets", "answers", kunci)) == \
            _read(os.path.join(str(tmp_path), "answers", kunci)), \
            "%s tidak mutakhir. Jalankan %s" % (kunci, PERINTAH["ws"])

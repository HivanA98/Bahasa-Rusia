"""Pengujian sistem Leitner: kenaikan kotak, jadwal, dan berkas progres."""

from __future__ import annotations

import datetime as dt
import json
import os

from rusdrill.leitner import (
    INTERVALS,
    MAX_BOX,
    MIN_BOX,
    CardState,
    Progress,
)

HARI = dt.date(2026, 1, 10)


def test_jawaban_benar_menaikkan_satu_kotak():
    st = CardState()
    assert st.box == MIN_BOX
    st.answer(True, HARI)
    assert st.box == 2
    st.answer(True, HARI)
    assert st.box == 3


def test_jawaban_salah_kembali_ke_kotak_satu():
    st = CardState(box=4)
    st.answer(False, HARI)
    assert st.box == MIN_BOX


def test_kotak_tidak_melebihi_batas():
    st = CardState(box=MAX_BOX)
    st.answer(True, HARI)
    assert st.box == MAX_BOX


def test_jeda_sesuai_tabel():
    for box in range(MIN_BOX, MAX_BOX + 1):
        st = CardState(box=box - 1 if box > MIN_BOX else MIN_BOX)
        st.box = box - 1 if box > MIN_BOX else MIN_BOX
        st.answer(True, HARI)
        harapan = HARI + dt.timedelta(days=INTERVALS[st.box])
        assert st.due == harapan.isoformat()


def test_jatuh_tempo_menurut_tanggal():
    st = CardState()
    st.answer(True, HARI)          # naik ke kotak 2, jeda 1 hari
    assert not st.is_due(HARI)
    assert st.is_due(HARI + dt.timedelta(days=1))
    assert st.is_due(HARI + dt.timedelta(days=5))


def test_simpan_dan_muat_ulang(tmp_path):
    path = str(tmp_path / "progress.json")
    p = Progress()
    p.record_answer("v001", True, HARI)
    p.record_answer("v002", False, HARI)
    p.settings["translit"] = True
    p.save(path)

    q = Progress.load(path)
    assert q.cards["v001"].box == 2
    assert q.cards["v002"].box == 1
    assert q.cards["v001"].correct == 1
    assert q.cards["v002"].wrong == 1
    assert q.settings["translit"] is True


def test_berkas_rusak_tidak_merusak_pemuatan(tmp_path):
    path = str(tmp_path / "progress.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write("{bukan json yang sah")
    p = Progress.load(path)
    assert p.cards == {}


def test_kartu_bernilai_aneh_diabaikan(tmp_path):
    path = str(tmp_path / "progress.json")
    data = {
        "version": 1,
        "cards": {
            "v001": {"box": 99, "due": "2026-01-01"},
            "v002": "bukan dict",
            "v003": {"box": "x", "due": "2026-01-01"},
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    p = Progress.load(path)
    assert p.cards["v001"].box == MAX_BOX    # dibatasi, bukan dipercaya mentah
    assert "v002" not in p.cards
    assert "v003" not in p.cards


def test_penulisan_atomik_tidak_meninggalkan_berkas_sementara(tmp_path):
    path = str(tmp_path / "progress.json")
    p = Progress()
    p.record_answer("v001", True, HARI)
    p.save(path)
    p.save(path)
    sisa = [f for f in os.listdir(str(tmp_path)) if f.endswith(".tmp")]
    assert not sisa, sisa


def test_ringkasan_kotak():
    p = Progress()
    p.record_answer("a", True, HARI)
    p.record_answer("b", True, HARI)
    p.record_answer("c", False, HARI)
    counts = p.box_counts(["a", "b", "c"])
    assert counts[1] == 1 and counts[2] == 2


def test_kartu_baru_dikenali():
    p = Progress()
    assert p.is_new("v001")
    p.record_answer("v001", True, HARI)
    assert not p.is_new("v001")
